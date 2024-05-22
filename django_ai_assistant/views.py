import json

from django.http import HttpRequest, JsonResponse
from django.utils.module_loading import import_string
from django.views import View

from openai import AsyncOpenAI

from .conf import settings


class AssistantViewMixin:
    def _call_setting_fn(self, dotted_path: str):
        fn = import_string(dotted_path)
        return fn(request=self.request)

    def get_ai_client(self) -> AsyncOpenAI:
        return self._call_setting_fn(dotted_path=settings.CLIENT_INIT_FN)

    def can_create_thread(self) -> bool:
        return self._call_setting_fn(dotted_path=settings.USER_CAN_CREATE_THREAD_FN)

    def can_create_message(self) -> bool:
        return self._call_setting_fn(dotted_path=settings.USER_CAN_CREATE_MESSAGE_FN)


class AssistantThreadListCreateView(AssistantViewMixin, View):
    async def create_thread(self):
        client = self.get_ai_client()
        return await client.beta.threads.create()

    async def post(self, request: HttpRequest, *args, **kwargs):
        if not self.can_create_thread():
            return JsonResponse({"error": "User is not allowed to create threads"}, status=403)

        thread = await self.create_thread()
        return JsonResponse(thread.to_dict())


class AssistantThreadMessageListCreateView(AssistantViewMixin, View):
    async def list_thread_messages(self):
        client = self.get_ai_client()
        async for message in client.beta.threads.messages.list(thread_id=self.kwargs["thread_id"]):
            yield message

    async def create_thread_message(self, content: str):
        client = self.get_ai_client()
        return await client.beta.threads.messages.create(
            thread_id=self.kwargs["thread_id"], role="user", content=content
        )

    async def create_run(self):
        client = self.get_ai_client()
        # TODO: manage assistants
        return await client.beta.threads.runs.create_and_poll(
            thread_id=self.kwargs["thread_id"], assistant_id="asst_Hc05cQHz22rDpHFbkGV9eVEN"
        )

    async def get(self, request: HttpRequest, *args, **kwargs):
        messages = []
        async for message in self.list_thread_messages():
            messages.append(message.to_dict())

        return JsonResponse({"object": "list", "data": messages})

    async def post(self, request: HttpRequest, *args, **kwargs):
        if not self.can_create_message():
            return JsonResponse({"error": "User is not allowed to create messages"}, status=403)
        try:
            body_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        if not body_data.get("content"):
            return JsonResponse({"error": "Message content is required"}, status=400)

        message = await self.create_thread_message(content=body_data["content"])
        run = await self.create_run()

        return JsonResponse(
            {
                "message": message.to_dict(),
                "run_id": run.to_dict(),
            }
        )
