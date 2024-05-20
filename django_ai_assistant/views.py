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

    async def create_thread_message(self):
        client = self.get_ai_client()
        return await client.beta.threads.messages.create(thread_id=self.kwargs["thread_id"])

    async def get(self, request: HttpRequest, *args, **kwargs):
        messages = []
        async for message in self.list_thread_messages():
            messages.append(message.to_dict())

        return JsonResponse({"object": "list", "data": messages})

    async def post(self, request: HttpRequest, *args, **kwargs):
        if not self.can_create_message():
            return JsonResponse({"error": "User is not allowed to create messages"}, status=403)

        message = await self.create_thread_message()
        return JsonResponse(message.to_dict())
