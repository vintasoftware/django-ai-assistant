const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  context: __dirname,
  entry: "./assets/js/index",
  output: {
    path: path.resolve(__dirname, "assets/webpack_bundles/"),
    // Cannot use publicPath: "auto" here because we need to specify the full URL,
    // since we're serving the files with the Webpack devServer:
    publicPath: "http://localhost:3000/webpack_bundles/",
    filename: "[name]-[contenthash].js",
  },
  devtool: "source-map",
  devServer: {
    hot: true,
    historyApiFallback: true,
    host: "localhost",
    port: 3000,
    // Allow CORS requests from the Django dev server domain:
    headers: { "Access-Control-Allow-Origin": "*" },
  },

  plugins: [
    new BundleTracker({ path: __dirname, filename: "webpack-stats.json" }),
    new MiniCssExtractPlugin(),
  ],

  module: {
    rules: [
      {
        test: /\.(js|jsx|tsx|ts)$/i,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      {
        test: /\.css$/i,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: {
              modules: {
                auto: true, // must be true for Mantine, as it uses both CSS modules and global CSS
                namedExport: false,
              },
              importLoaders: 1, // 1 => postcss-loader
            },
          },
          "postcss-loader",
        ],
      },
    ],
  },

  resolve: {
    extensions: [".js", ".ts", ".jsx", ".tsx"],
    alias: {
      "@": path.resolve(__dirname, "assets/js"),
      // Necessary to deduplicate React due to pnpm link:
      react: path.resolve("./node_modules/react"),
    },
  },
};
