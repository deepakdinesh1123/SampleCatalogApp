const HtmlWebpackPlugin = require("html-webpack-plugin");
const path = require("path");
const webpack = require("webpack");

module.exports = {
  entry: {
    main: [
      "script-loader!../static/js/webfont/1.6.26/webfont.js",
      "script-loader!../static/js/tinycolor/1.6.0/tinycolor.min.js",
      "script-loader!../static/js/popper/2.11.8/popper.min.js",
      "../static/js/webpack.js",
    ],
  },
  module: {
    rules: [
      {
        test: /\.svg$/,
        use: "svg-inline-loader",
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ],
  },
  output: {
    path: path.resolve(__dirname, "../static/js"),
    filename: getVersionedFileName(),
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
    // new HtmlWebpackPlugin({
    //   filename: path.resolve(__dirname, "../templates/frame/_base.html"),
    //   template: "../static/template.html",
    //   inject: false,
    //   publicPath: "packages/frame/js/",
    // }),
  ],
  mode: "production",
};

function getVersionedFileName() {
  const manifestPath = path.resolve(__dirname, "../manifest.json");
  const manifest = require(manifestPath);

  if (manifest && manifest.version) {
    return `frame.${manifest.version}.min.js`;
  }

  console.error(
    `Error: Unable to read version from manifest.json at path: ${manifestPath}`
  );
  return "frame.min.js"; // Default filename if version is not available
}
