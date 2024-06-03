// Base Html Script
let link = document.querySelector("link[rel~='icon']");
if (!link) {
  link = document.createElement("link");
  link.rel = "icon";
  document.head.appendChild(link);
}

link.href = frame_config.fav_icon;

window.onload = (event) => {
  let frameLoader = document.querySelector(".frame-loader");
  frameLoader.classList.remove("overlay-spinner");
};
