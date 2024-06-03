// Web Component for Frame
class Frame extends HTMLElement {
  constructor() {
    super();
    const shadow = this.attachShadow({ mode: "open" });

    WebFont.load({
      google: {
        families: ["Lato:100,300,400,600,700"],
      },
    });
  }

  connectedCallback() {
    const config = JSON.parse(this.getAttribute("config"));
    const app_theme_config = JSON.parse(this.getAttribute("app_theme_config"));

    let newAppThemeConfig = {
      color: {
        accent:
          app_theme_config?.color?.primary ||
          config?.config?.color?.primary ||
          "#DDE2E5",
        header: "#FFFFFF",
        primary:
          app_theme_config?.color?.primary ||
          config?.config?.color?.primary ||
          "#DDE2E5",
        sidebar:
          app_theme_config?.color?.secondary ||
          config?.config?.color?.secondary ||
          "#E1D6AE",
        secondary:
          app_theme_config?.color?.secondary ||
          config?.config?.color?.secondary ||
          "#E1D6AE",
        background:
          app_theme_config?.color?.background ||
          config?.config?.color?.background ||
          "#FFFFFF",
        typography: "#212429",
        headerBorder: "#DDE2E5",
      },
    };
    this.render({ ...config, config: newAppThemeConfig });
  }

  render(config) {
    const pathname = window.location.pathname;
    const template = document.createElement("template");

    let drawerType;
    let baseUrl = "/api/v1/profile/";

    function getCookie(name) {
      var cookieArray = document.cookie.split(";");
      for (var i = 0; i < cookieArray.length; i++) {
        var cookie = cookieArray[i].trim();
        if (cookie.indexOf(name + "=") === 0) {
          return cookie.substring(name.length + 1, cookie.length);
        }
      }
      return null;
    }

    template.innerHTML = `
          <style>
            // Boostrap Css
            .container, .container-fluid, .container-lg, .container-md, .container-sm, .container-xl, .container-xxl {
              --bs-gutter-x: 1.5rem;
              --bs-gutter-y: 0;
              width: 100%;
              padding-right: calc(var(--bs-gutter-x) * .5);
              padding-left: calc(var(--bs-gutter-x) * .5);
              margin-right: auto;
              margin-left: auto;
            }

            .d-flex {
                display: flex!important;
            }

            .vh-100 {
                height: 100vh!important;
            }

            .flex-column {
                flex-direction: column!important;
            }

            .flex-grow-1 {
                flex-grow: 1!important;
            }

            .p-0 {
                padding: 0!important;
            }

            .align-items-center {
                align-items: center!important;
            }

            .justify-content-between {
                justify-content: space-between!important;
            }

            *, ::after, ::before {
                box-sizing: border-box;
            }

            .overflow-y-auto {
                overflow-y: auto!important;
            }

            .nav {
                --bs-nav-link-padding-x: 1rem;
                --bs-nav-link-padding-y: 0.5rem;
                --bs-nav-link-font-weight: ;
                --bs-nav-link-color: var(--bs-link-color);
                --bs-nav-link-hover-color: var(--bs-link-hover-color);
                --bs-nav-link-disabled-color: var(--bs-secondary-color);
                display: flex;
                flex-wrap: wrap;
                padding-left: 0;
                margin-top: 0;
                margin-bottom: 0;
                list-style: none;
            }

            .position-relative {
                position: relative!important;
            }

            .dropdown, .dropdown-center, .dropend, .dropstart, .dropup, .dropup-center {
                position: relative;
            }

            .btn {
              --bs-btn-padding-x: 0.75rem;
              --bs-btn-padding-y: 0.375rem;
              --bs-btn-font-family: ;
              --bs-btn-font-size: 1rem;
              --bs-btn-font-weight: 400;
              --bs-btn-line-height: 1.5;
              --bs-btn-color: var(--bs-body-color);
              --bs-btn-bg: transparent;
              --bs-btn-border-width: var(--bs-border-width);
              --bs-btn-border-color: transparent;
              --bs-btn-border-radius: var(--bs-border-radius);
              --bs-btn-hover-border-color: transparent;
              --bs-btn-box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15),0 1px 1px rgba(0, 0, 0, 0.075);
              --bs-btn-disabled-opacity: 0.65;
              --bs-btn-focus-box-shadow: 0 0 0 0.25rem rgba(var(--bs-btn-focus-shadow-rgb), .5);
              display: inline-block;
              padding: var(--bs-btn-padding-y) var(--bs-btn-padding-x);
              font-family: var(--bs-btn-font-family);
              font-size: var(--bs-btn-font-size);
              font-weight: var(--bs-btn-font-weight);
              line-height: var(--bs-btn-line-height);
              color: var(--bs-btn-color);
              text-align: center;
              text-decoration: none;
              vertical-align: middle;
              cursor: pointer;
              -webkit-user-select: none;
              -moz-user-select: none;
              user-select: none;
              border: var(--bs-btn-border-width) solid var(--bs-btn-border-color);
              border-radius: var(--bs-btn-border-radius);
              background-color: var(--bs-btn-bg);
              transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;
          }

          .dropdown-menu {
              --bs-dropdown-zindex: 1000;
              --bs-dropdown-min-width: 10rem;
              --bs-dropdown-padding-x: 0;
              --bs-dropdown-padding-y: 0.5rem;
              --bs-dropdown-spacer: 0.125rem;
              --bs-dropdown-font-size: 1rem;
              --bs-dropdown-color: var(--bs-body-color);
              --bs-dropdown-bg: var(--bs-body-bg);
              --bs-dropdown-border-color: var(--bs-border-color-translucent);
              --bs-dropdown-border-radius: var(--bs-border-radius);
              --bs-dropdown-border-width: var(--bs-border-width);
              --bs-dropdown-inner-border-radius: calc(var(--bs-border-radius) - var(--bs-border-width));
              --bs-dropdown-divider-bg: var(--bs-border-color-translucent);
              --bs-dropdown-divider-margin-y: 0.5rem;
              --bs-dropdown-box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
              --bs-dropdown-link-color: var(--bs-body-color);
              --bs-dropdown-link-hover-color: var(--bs-body-color);
              --bs-dropdown-link-hover-bg: var(--bs-tertiary-bg);
              --bs-dropdown-link-active-color: #fff;
              --bs-dropdown-link-active-bg: #0d6efd;
              --bs-dropdown-link-disabled-color: var(--bs-tertiary-color);
              --bs-dropdown-item-padding-x: 1rem;
              --bs-dropdown-item-padding-y: 0.25rem;
              --bs-dropdown-header-color: #6c757d;
              --bs-dropdown-header-padding-x: 1rem;
              --bs-dropdown-header-padding-y: 0.5rem;
              position: absolute;
              z-index: var(--bs-dropdown-zindex);
              display: none;
              min-width: var(--bs-dropdown-min-width);
              padding: var(--bs-dropdown-padding-y) var(--bs-dropdown-padding-x);
              margin: 0;
              font-size: var(--bs-dropdown-font-size);
              color: var(--bs-dropdown-color);
              text-align: left;
              list-style: none;
              background-color: var(--bs-dropdown-bg);
              background-clip: padding-box;
              border: var(--bs-dropdown-border-width) solid var(--bs-dropdown-border-color);
              border-radius: var(--bs-dropdown-border-radius);
          }

          .dropdown-item {
              display: block;
              width: 100%;
              padding: var(--bs-dropdown-item-padding-y) var(--bs-dropdown-item-padding-x);
              clear: both;
              font-weight: 400;
              color: var(--bs-dropdown-link-color);
              text-align: inherit;
              text-decoration: none;
              white-space: nowrap;
              background-color: transparent;
              border: 0;
              border-radius: var(--bs-dropdown-item-border-radius,0);
          }

          hr {
              margin: 1rem 0;
              color: inherit;
              border: 0;
              opacity: .25;
          }
            :host {
                --primary-color: ${
                  tinycolor(config?.config?.color?.primary).toHexString() ||
                  "#DDE2E5"
                };
                --primary-light-color: ${tinycolor
                  .mix(
                    tinycolor(config?.config?.color?.primary).toHexString(),
                    "#FFFFFF",
                    90
                  )
                  .toHexString()};
                --secondary-color: ${
                  tinycolor(config?.config?.color?.secondary).toHexString() ||
                  "#E1D6AE"
                };
                --accent-color: ${
                  tinycolor(config?.config?.color?.accent).toHexString() ||
                  "#DDE2E5"
                };
                --background-color: ${
                  tinycolor(config?.config?.color?.background).toHexString() ||
                  "#FFFFFF"
                };
                --typography-color: ${
                  tinycolor(config?.config?.color?.typography).toHexString() ||
                  "#212429"
                };
                --top-navbar-color: ${
                  tinycolor(config?.config?.color?.header).isLight()
                    ? tinycolor(
                        config?.config?.color?.typography
                      ).toHexString() || "#212429"
                    : "#FFFFFF"
                };
                --top-navbar-background-color: ${
                  tinycolor(config?.config?.color?.header).toHexString() ||
                  "#FFFFFF"
                };
                --top-navbar-border-color: ${
                  tinycolor(
                    config?.config?.color?.headerBorder
                  ).toHexString() || "#DDE2E5"
                };
                --side-navbar-color: ${
                  tinycolor(config?.config?.color?.sidebar).isLight()
                    ? tinycolor(
                        config?.config?.color?.typography
                      ).toHexString() || "#212429"
                    : "#FFFFFF"
                };
                --side-navbar-background-color: ${
                  tinycolor(config?.config?.color?.sidebar).toHexString() ||
                  "#E1D6AE"
                };
                --side-navbar-hover-background-color: ${
                  tinycolor(config?.config?.color?.sidebar).isLight()
                    ? tinycolor
                        .mix(
                          tinycolor(
                            config?.config?.color?.sidebar
                          ).toHexString(),
                          "#000000",
                          6
                        )
                        .toHexString() || "#E1D6AE"
                    : tinycolor
                        .mix(
                          tinycolor(
                            config?.config?.color?.sidebar
                          ).toHexString(),
                          "#FFFFFF",
                          6
                        )
                        .toHexString() || "#FFFFFF"
                };
                --gap: 0px;
            }

              .complete-hidden-scroll-style::-webkit-scrollbar-track {
                  -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
                  border-radius: 10px;
                  background-color: transparent;
              }

              .complete-hidden-scroll-style::-webkit-scrollbar {
                  width: 0px;
                  background-color: transparent;
              }

              .complete-hidden-scroll-style::-webkit-scrollbar-thumb {
                  border-radius: 10px;
                  -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.3);
                  background-color: #555;
              }

              .frame-page {
                background-color: var(--background-color);
                overflow-y: auto;
              }

            .frame-navbar {
                position: relative;
                padding: 8px 40px 8px 24px; 
                border-bottom: 1px solid var(--top-navbar-border-color);
                background-color: var(--top-navbar-background-color);
                z-index: 10;
            }

            .frame-side-navbar {
                display: flex;
                flex-direction: column;
                flex-wrap: nowrap;
                overflow-y: auto;
                z-index: 6;
                width: ${config?.display_sidebar === false ? "0px" : "88px"};
                min-width: ${
                  config?.display_sidebar === false ? "0px" : "88px"
                };
                max-width: ${
                  config?.display_sidebar === false ? "0px" : "88px"
                };
                padding-top: 12px;
                background-color: var(--side-navbar-background-color);
            }

            .mobile-frame-side-navbar-modal {
                position: fixed;
                top: 0px;
                display: flex;
                z-index: -1;
                width: 100vw;
                height: 100vh;
                opacity: 0%;
                background: linear-gradient(126deg, rgba(0, 0, 0, 0.80) 0%, rgb(0 0 0 / 73%) 70.87%);
                transition: width .4s ease-in, opacity .4s ease-in;
            }
            
            .open {
              display: flex;
              width: 100vw;
              opacity: 100%;
              z-index: 10;
            }

            .mobile-frame-side-navbar-modal.open > .mobile-frame-side-navbar {
              width: 100%;
              min-width: calc(100% - 40px);
              max-width: calc(100% - 40px);
            }

            .mobile-frame-side-navbar {
                position: relative;
                display: flex;
                flex-direction: column;
                flex-wrap: nowrap;
                overflow-y: auto;
                width: 0%;
                min-width: 0%;
                max-width: 0%;
                height: 100vh;
                padding-top: 98px;
                background-color: var(--side-navbar-background-color);
                transition: width .4s ease-out, min-width .4s ease-out, max-width .4s ease-out;
            }
            
            .open-mobile-frame-side-navbar {
                display: none;
                background: transparent;
                border: 0px;
                padding: 0px;
                margin: 0px;
            }

            .close-mobile-frame-side-navbar {
                position: absolute;
                top: 50px;
                right: 16px;
                background: transparent;
                border: 0px;
                padding: 0px;
                margin: 0px;
            }

            .gap {
                gap: var(--gap);
            }

            .small-device-height-fix2 {
                max-height: 100vh;
                max-height: calc(100vh - 41px);
                height: 100%;
            }

            .each-mobile-frame-link {
                padding: 10px 24px 10px 24px;
                text-decoration: none;
            }

            .each-frame-link {
                padding: 10px 0px 10px 0px;
                text-decoration: none;
            }

            .each-frame-link:hover {
                height: fit-content;
                max-height: min-content;
                background-color: var(--side-navbar-hover-background-color);
            }

            .each-frame-menu-label {
                color: var(--side-navbar-color);
                text-align: center;
                font-family: 'Lato';
                font-size: 10px;
                font-style: normal;
                font-weight: 700;
                line-height: 12px;
                letter-spacing: 0.2px;
            }

            .profile-dropdown-menu {
              min-width: 227px;
              padding: 4px;
              border-radius: 4px;
              background: var(--neutral-light-white, #FFF) !important;
              box-shadow: 0px 4px 24px 0px rgba(0, 0, 0, 0.16);
          }
  
          .profile-dropdown-menu .dropdown-item {
              border-radius: 2px;
              padding: 12px 12px 12px 20px;
          }
  
          .profile-dropdown-menu .dropdown-item:hover,
          .profile-dropdown-menu .dropdown-item:active,
          .profile-dropdown-menu .dropdown-item:focus {
              background-color: #F0F3F4;
          }
  
          .profile-info {
              margin-bottom: 4px;
          }
  
  
          .profile-name, .profile-menu-name {
              color: var(--typography-color);
              font-family: Lato;
              font-size: 14px;
              font-style: normal;
              font-weight: 700;
              line-height: 20px;
              letter-spacing: 0.2px;
          }

          .profile-logout-name {
              color: #AA2113;
              font-family: Lato;
              font-size: 14px;
              font-style: normal;
              font-weight: 700;
              line-height: 20px;
              letter-spacing: 0.2px;
          }
  
          .profile-role {
              color: var(--neutral-mid-mid-500, #6C747D);
              font-family: Lato;
              font-size: 12px;
              font-style: normal;
              font-weight: 400;
              line-height: 16px;
              letter-spacing: 0.2px;
          }
  
          .profile-dropdown-divider {
              margin: 0px;
              height: 1px;
              border-radius: 2px;
              background: var(--neutral-light-light-200, #DDE2E5);
          }
  
          .profile-roles {
              display: flex;
              flex-direction: column;
              padding: 12px 0px;
              overflow-y: auto;
              max-height: 248px;
          }
  
          .profile-roles .dropdown-item {
              padding: 4px 12px 4px 20px;
          }
  
          .profile-each-role .label {
              color: var(--typography-color);
              font-family: Lato;
              font-size: 14px;
              font-style: normal;
              font-weight: 400;
              line-height: 20px;
              letter-spacing: 0.2px;
          }
          
          .profile-menu-option {
            margin: 4px 0px;
            cursor: pointer;
          }

          .profile-logout {
              color: #AA2113;
              margin: 4px 0px;
          }

          .each-frame-link {
              padding: 10px 0px 10px 0px;
              text-decoration: none;
          }
  
          .each-frame-link:hover {
              height: fit-content;
              max-height: min-content;
              background-color: var(--side-navbar-hover-background-color);
          }
          
          .focused-frame-parent-menu, .selected-each-frame-menu, .selected-each-frame-submenu {
              background-color: var(--side-navbar-hover-background-color);
              position: relative;
          }

          .selected-each-frame-submenu::before {
              content: "";
              position: absolute;
              width: 4px;
              height: 4px;
              top: calc(50% - 2px);
              left: 8px;
              border-radius: 50%;
              background-color: var(--side-navbar-color);
          }
  
          .each-frame-menu-label {
              color: var(--side-navbar-color);
              text-align: center;
              font-family: 'Lato';
              font-size: 10px;
              font-style: normal;
              font-weight: 700;
              line-height: 12px;
              letter-spacing: 0.2px;
          }

          .mobile-each-frame-menu-label {
              color: var(--side-navbar-color);
              text-align: center;
              font-family: 'Lato';
              font-size: 16px;
              font-style: normal;
              font-weight: 700;
              line-height: 20px;
              letter-spacing: 0.2px;
          }
  
          .frame-sidenav-dropdown-menu {
              display: flex;
              flex-direction: column;
              min-width: 227px;
              padding: 4px;
              border-radius: 4px;
              background: var(--side-navbar-background-color) !important;
              box-shadow: -4px 4px 8px 0px rgba(0, 0, 0, 0.15);
              border: 0px;
              gap: 6px;
          }
  
          .frame-sidenav-dropdown-menu .dropdown-item {
              border-radius: 2px;
              padding: 4px 4px 4px 20px;
              display: flex;
          }
  
          .frame-sidenav-dropdown-menu .dropdown-item:hover,
          .frame-sidenav-dropdown-menu .dropdown-item:active,
          .frame-sidenav-dropdown-menu .dropdown-item:focus {
              background-color: var(--side-navbar-hover-background-color);
          }

          .mobile-frame-sidenav-dropdown-menu {
              position: relative;
              display: flex;
              flex-direction: column;
              width: 100%;
              padding: 4px 0px 12px 0px;
              background: transparent;
              border: 0px;
          }

          .mobile-frame-sidenav-dropdown-menu .dropdown-item {
              padding: 8px 0px 8px 80px;
              display: flex;
              background-color: var(--side-navbar-hover-background-color);
          }

          .mobile-frame-sidenav-dropdown-menu .dropdown-item:hover,
          .mobile-frame-sidenav-dropdown-menu .dropdown-item:active,
          .mobile-frame-sidenav-dropdown-menu .dropdown-item:focus {
              background-color: var(--side-navbar-hover-background-color);
          }
  
          .each-frame-submenu-label {
              color: var(--side-navbar-color);
              font-family: Lato;
              font-size: 11px;
              font-style: normal;
              font-weight: 400;
              line-height: 16px;
              letter-spacing: 0.2px;
          }

          .each-mobile-frame-submenu-label {
            color: #766e54;
            text-align: center;
            font-family: 'Lato';
            font-size: 16px;
            font-style: normal;
            font-weight: 700;
            line-height: 20px;
            letter-spacing: 0.2px;
        }
  
          .frame-sidenav-menu-arrow {
              display: flex;
              position: absolute;
              bottom: 2px;
              right: 2px;
              height: 6px;
          }

          .mobile-frame-sidenav-menu-arrow {
              display: flex;
              position: absolute;
              top: calc(50% - 10px);
              right: 24px;
              height: 20px;
              transform: rotate(0deg);
              transition: transform .4s ease-out;
          }

          .rotate-arrow {
            transform: rotate(180deg);
          }
         
          .sideDrawerContainer {
            height: 100%;
            width: 0%; 
            position: fixed; 
            z-index: 12; 
            top: 0;
            right: 0;
            background-color: #fff; 
            overflow-x: hidden; 
          }

          .content-container {
            padding-top: 32px;
            padding-bottom: 32px;
            height: 100%;
            position: relative;
            display: flex;
            flex-direction: column;
          }

          .content-container form {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
          }
         
          .sideDrawerContainer a {
            padding: 8px 8px 8px 32px;
            text-decoration: none;
            font-size: 25px;
            color: #818181;
            display: block;
          }

         
          .sideDrawerContainer a:hover {
            color: #f1f1f1;
          }

         
          .closebtn {
            position: absolute;
            top: 0;
            right: 25px;
            font-size: 36px;
            cursor: pointer;
            z-index: 4;
            background-color: transparent;
            border: 0px;
          }

          .drawer-backdrop {
            display: none;
            background-color: #000000bf;
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 11;
          }

          .drawer-content {
            margin-top: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            height: 100%;
          }

          #drawer-form {
            margin-left: 32px;
            margin-right: 32px;
          }

           .drawer-header {
            font-size: 22px;
            font-style: normal;
            font-weight: 600;
            line-height: 28px; /* 127.273% */
            letter-spacing: -0.2px;
            margin-left: 32px;
            margin-right: 32px;
            margin-bottom: 16px;
          }

          .drawer-server-error-text {
            color: white;
          }

          .form-label {
            font-size: 12px;
            font-style: normal;
            font-weight: 600;
            line-height: normal;
            letter-spacing: 0.48px;
            color: #A3ABB1;
          }

          .drawer-input {
            border-radius: 6px;
            border: 1px solid var(--neutral-light-light-200, #DDE2E5);
            padding: 16px;
            width: 100%;
          }

          .form-field-container {
            display: flex;
            flex-direction: column;
            gap: 4px;
          }

          .drawer-submit {
            width: 100%;
          }

          .drawer-error {
            font-size: 12px;
            color: #D52918;
            display: none;
          }

          .server-drawer-error{
            background-color: #D52918;
            font-family: Lato;
            font-size: 11px;
            font-style: normal;
            font-weight: 700;
            line-height: 16px; /* 145.455% */
            letter-spacing: 0.4px;
            text-transform: uppercase;
            color: white;
            display: none;
            align-items: center;
            gap: 8px;
            padding: 16px 24px;
          }

          .submit-button {
            height: 42px;
            width: 100%;
            padding: 7px 16px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
            border-radius: 4px;
            border: none;
            font-size: 14px;
            font-style: normal;
            font-weight: 700;
            line-height: 20px; 
            letter-spacing: 0.2px;
            color: #fff;
            background: var(--primary-color, #5048ED);
          }

          .profileDrawerContainer {
            height: calc(100% - 43px);
            width: 0%; 
            position: fixed; 
            z-index: 5; 
            bottom: 0;
            right: 0;
            background-color: #fff; 
            overflow-x: hidden; 
          }

          .btn-close {
            position: absolute;
            top: 0.5em;
            right: 2em;
            box-sizing: content-box;
            width: 1em;
            height: 1em;
            padding: 0.25em 0.25em;
            color: #000;
            border: 0;
            border-radius: 0.25rem;
            cursor: pointer;
            background: transparent;
          }

          .profile-drawer-container {
            padding: 24px 40px;
            display: flex;
          }


          .profile-drawer-title {
              font-family: Lato;
              font-size: 10px;
              font-weight: 800;
              line-height: 12px;
              letter-spacing: 0.2em;
              color: #212429;
          }

          .profile-name-container {
              display: flex;
              gap: 24px;
              margin-top: 46px;
              align-items: center;
          }

          .change-password-btn {
              font-family: Lato;
              font-size: 14px;
              font-weight: 700;
              line-height: 20px;
              letter-spacing: 0.20000000298023224px;
              text-align: left;
              padding: 11px 16px;
              background-color: transparent;
              border-radius: 4px;
              border: 1px solid var(--primary-color, #5048ED);
              color: var(--primary-color, #5048ED);
              cursor: pointer;
          }

          .profile-name-change-password-container {
              display: flex;
              flex-direction: column;
              gap: 12px;
          }

          .user-name {
              font-family: Source Sans Pro;
              font-size: 22px;
              font-weight: 600;
              line-height: 28px;
              letter-spacing: -0.20000000298023224px;
              text-align: left;
          }

          .profile-detail-container {
              gap: 8px;
              margin-top: 40px;
              display: flex;
              flex-direction: column;
          }

          .profile-detial-label-container {
              flex-direction: column;
              justify-content: flex-start;
              align-items: flex-start;
              gap: 24px;
              display: inline-flex
          }

          .profile-detail-label-text {
              color: #6C747D;
              font-size: 14px;
              font-family: Lato;
              font-weight: 400;
              line-height: 20px;
              letter-spacing: 0.20px;
              word-wrap: break-word;

          }

          .profile-detail-individual-data-container {
              grid-template-columns: 1fr 1fr;
              display: grid;
          }

          .profile-detail-individual-label {
              flex-direction: column;
              justify-content: flex-start;
              align-items: flex-start;
              gap: 8px;
              display: inline-flex;
              width: 150px;
          }

          .profile-detail-individual-label-text {
              color: #A3ABB1;
              font-size: 14px;
              font-family: Lato;
              font-weight: 400;
              line-height: 20px;
              letter-spacing: 0.20px;
              word-wrap: break-word
          }

          .profile-detail-individual-label-data-container {
              flex-direction: column;
              justify-content: flex-start;
              align-items: flex-start;
              gap: 8px;
              display: inline-flex
          }

          .profile-detail-individual-label-data-text {
              color: #212429;
              font-size: 14px;
              font-family: Lato;
              font-weight: 700;
              line-height: 20px;
              letter-spacing: 0.20px;
              word-wrap: break-word
          }

          @media screen and (max-height: 450px) {
            .sideDrawerContainer {padding-top: 15px;}
            .sideDrawerContainer a {font-size: 18px;}
          }

          @media screen and (max-width: 640px) {
            .frame-side-navbar {
              display: none;
            }

            .open-mobile-frame-side-navbar {
              display: ${config?.display_sidebar === false ? "none" : "flex"};
            }

            .profile-arrow {
              display: none;
            }
          }
        </style>
        <div class="container-fluid d-flex flex-column p-0 vh-100 flex-grow-1" id="frame-container">
            <nav class="d-flex align-items-center justify-content-between frame-navbar">
                <button type="button" class="btn open-mobile-frame-side-navbar">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M17.875 3C18.4964 3 19 3.48963 19 4.09375C19 4.69787 18.4964 5.1875 17.875 5.1875H2.125C1.50362 5.1875 1 4.69787 1 4.09375C1 3.48963 1.50362 3 2.125 3H17.875ZM17.875 8.90625C18.4964 8.90625 19 9.39588 19 10C19 10.6041 18.4964 11.0938 17.875 11.0938H2.125C1.50362 11.0938 1 10.6041 1 10C1 9.39588 1.50362 8.90625 2.125 8.90625H17.875ZM17.875 14.8125C18.4964 14.8125 19 15.3021 19 15.9062C19 16.5104 18.4964 17 17.875 17H2.125C1.50362 17 1 16.5104 1 15.9062C1 15.3021 1.50362 14.8125 2.125 14.8125H17.875Z" fill="black"/>
                  </svg>
                </button>
                <div class="d-flex align-items-center justify-content-between gap" style="--gap: 48px">
                ${
                  config?.logo
                    ? `<img src=${config?.logo} height="32px" alt="#"/>`
                    : `<svg xmlns="http://www.w3.org/2000/svg" width="62" height="20" viewBox="0 0 62 20" fill="none">
                <path d="M0 15.5495L0 13.7372L5.34244 6.80918L0.527365 6.80918L0.527365 4.17101L9.53843 4.17101L9.53843 5.96037L4.19599 12.9114L9.69894 12.9114V15.5495L0 15.5495Z" fill="var(--top-navbar-color)"/>
                <path d="M16.605 15.8248C15.7949 15.8248 15.0382 15.6948 14.3351 15.4348C13.6319 15.1595 13.0205 14.7695 12.5007 14.2649C11.981 13.7449 11.5759 13.1178 11.2855 12.3837C10.9951 11.6496 10.8499 10.8085 10.8499 9.86027C10.8499 8.94265 11.0027 8.11679 11.3084 7.38269C11.6142 6.6333 12.0116 6.00626 12.5007 5.50156C13.0052 4.98158 13.5784 4.58394 14.2204 4.30865C14.8624 4.03337 15.5274 3.89573 16.2152 3.89573C17.0254 3.89573 17.7285 4.03337 18.3247 4.30865C18.9361 4.58394 19.4406 4.96628 19.838 5.45568C20.2507 5.94508 20.5564 6.52624 20.7552 7.19916C20.9539 7.85679 21.0532 8.5756 21.0532 9.35558C21.0532 9.66145 21.0379 9.95203 21.0074 10.2273C20.9768 10.5026 20.9462 10.7091 20.9157 10.8467L14.1058 10.8467C14.2586 11.6726 14.5949 12.2843 15.1146 12.682C15.6497 13.0643 16.2993 13.2555 17.0636 13.2555C17.8738 13.2555 18.6916 13.0031 19.517 12.4984L20.6405 14.5401C20.0596 14.9378 19.41 15.2513 18.6916 15.4807C17.9884 15.7101 17.2929 15.8248 16.605 15.8248ZM14.0828 8.62148L18.1871 8.62148C18.1871 7.97914 18.0419 7.45916 17.7515 7.06152C17.461 6.66389 16.9719 6.46507 16.284 6.46507C15.749 6.46507 15.2751 6.64094 14.8624 6.9927C14.465 7.34445 14.2051 7.88738 14.0828 8.62148Z" fill="var(--top-navbar-color)"/>
                <path d="M26.4777 15.8248C25.8969 15.8248 25.4077 15.7331 25.0103 15.5495C24.6128 15.366 24.2918 15.1137 24.0472 14.7925C23.818 14.456 23.6498 14.0584 23.5428 13.5996C23.4358 13.1255 23.3823 12.5978 23.3823 12.0167L23.3823 0L26.7529 0L26.7529 12.1543C26.7529 12.5061 26.814 12.7508 26.9363 12.8884C27.0739 13.0261 27.2114 13.0949 27.349 13.0949C27.4254 13.0949 27.4866 13.0949 27.5324 13.0949C27.5936 13.0949 27.67 13.0796 27.7617 13.049L28.1745 15.5495C27.991 15.626 27.7541 15.6872 27.4637 15.7331C27.1885 15.7942 26.8599 15.8248 26.4777 15.8248Z" fill="var(--top-navbar-color)"/>
                <path d="M34.3225 15.8248C33.6193 15.8248 33.0155 15.7178 32.5111 15.5036C32.0219 15.2895 31.6168 14.9913 31.2958 14.609C30.9901 14.2266 30.7608 13.7678 30.608 13.2325C30.4704 12.682 30.4016 12.0779 30.4016 11.4202L30.4016 6.80918L28.8424 6.80918V4.30865L30.585 4.17101L30.9748 1.14286L33.7722 1.14286V4.17101L36.5007 4.17101V6.80918L33.7722 6.80918V11.3743C33.7722 12.0167 33.9021 12.4831 34.162 12.7737C34.4371 13.049 34.7963 13.1867 35.2396 13.1867C35.423 13.1867 35.6065 13.1637 35.7899 13.1178C35.9886 13.0719 36.1644 13.0184 36.3173 12.9572L36.8446 15.4119C36.5389 15.5036 36.1797 15.5954 35.767 15.6872C35.3543 15.7789 34.8727 15.8248 34.3225 15.8248Z" fill="var(--top-navbar-color)"/>
                <path d="M38.7205 15.5495V0L42.0911 0V3.41397L41.9306 5.45568C42.3586 5.07334 42.8554 4.72158 43.4209 4.40042C43.9865 4.06396 44.6591 3.89573 45.4387 3.89573C46.6768 3.89573 47.5711 4.30101 48.1214 5.11157C48.687 5.92214 48.9697 7.04623 48.9697 8.48384V15.5495H45.5992V8.91971C45.5992 8.09385 45.4845 7.52798 45.2553 7.22211C45.0413 6.91623 44.6897 6.7633 44.2005 6.7633C43.7725 6.7633 43.4057 6.8627 43.0999 7.06152C42.7942 7.24505 42.4579 7.51269 42.0911 7.86444V15.5495H38.7205Z" fill="var(--top-navbar-color)"/>
                <path d="M53.0807 20C52.7291 20 52.431 19.9771 52.1864 19.9312C51.9418 19.9006 51.7049 19.8471 51.4756 19.7706L52.0718 17.2013C52.1788 17.2318 52.3011 17.2624 52.4386 17.293C52.5762 17.3236 52.7061 17.3389 52.8284 17.3389C53.394 17.3389 53.8297 17.2013 54.1354 16.926C54.4411 16.6507 54.6704 16.2913 54.8233 15.8478L54.9837 15.2513L50.6043 4.17101L53.9978 4.17101L55.6258 9.05735C55.7939 9.57734 55.9468 10.105 56.0843 10.6402C56.2219 11.1755 56.3671 11.7261 56.52 12.292H56.6117C56.734 11.7567 56.8563 11.2214 56.9786 10.6861C57.1161 10.1356 57.2537 9.59263 57.3913 9.05735L58.767 4.17101H62L58.0562 15.6642C57.7811 16.383 57.4906 17.0101 57.1849 17.5454C56.8945 18.0959 56.5506 18.5471 56.1531 18.8989C55.771 19.2659 55.3277 19.5412 54.8233 19.7247C54.3341 19.9082 53.7532 20 53.0807 20Z" fill="var(--top-navbar-color)"/>
            </svg>`
                }
                    
                </div>
                <div class="d-flex align-items-center gap" style="--gap: 40px">
                <div class="dropdown profile-dropdown-menu-button">
                <div class="btn" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="true"
                    style="--bs-btn-padding-x:0px;--bs-btn-padding-y:0px;border:0px">
                    <div class="d-flex align-items-center gap" style="--gap: 8px">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <g clip-path="url(#clip0_5506_359)">
                                <path
                                    d="M12.0001 0.599976C5.71234 0.599976 0.600098 5.71222 0.600098 12C0.600098 18.2877 5.71234 23.4 12.0001 23.4C18.2879 23.4 23.4001 18.2877 23.4001 12C23.4001 5.71222 18.2879 0.599976 12.0001 0.599976ZM12.0001 7.12774C13.9679 7.12774 15.5756 8.73554 15.5756 10.7033C15.5756 12.6711 13.9678 14.2788 12.0001 14.2788C10.0324 14.2788 8.42458 12.671 8.42458 10.7033C8.42458 8.73545 10.0324 7.12774 12.0001 7.12774ZM5.7601 18.9122V18.3844C5.7601 16.8722 6.98448 15.6244 8.5201 15.6244H15.4801C16.9923 15.6244 18.2401 16.8488 18.2401 18.3844V18.9122C16.5845 20.4 14.4001 21.3122 12.0001 21.3122C9.6001 21.3122 7.41562 20.4 5.7601 18.9122Z"
                                    fill="var(--top-navbar-color)" />
                            </g>
                            <defs>
                                <clipPath id="clip0_5506_359">
                                    <rect width="24" height="24" fill="white" />
                                </clipPath>
                            </defs>
                        </svg>
                        <div class="profile-arrow">
                          <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10" fill="none">
                          <path fill-rule="evenodd" clip-rule="evenodd"
                          d="M1.87107 2.85549C1.65751 2.64192 1.31124 2.64192 1.09768 2.85549C0.884108 3.06906 0.884108 3.41532 1.09768 3.62889L4.6133 7.14451C4.64 7.17121 4.66877 7.19457 4.69909 7.21459C4.91136 7.35474 5.19983 7.33138 5.3867 7.14451L8.90232 3.62889C9.11589 3.41532 9.11589 3.06906 8.90232 2.85549C8.68876 2.64192 8.34249 2.64192 8.12893 2.85549L5 5.98441L1.87107 2.85549Z"
                          fill="var(--top-navbar-color)" />
                          </svg>
                        </div>
                    </div>
                </div>
          
                <ul class="dropdown-menu profile-dropdown-menu">
                    <li id="profile-info"><a class="dropdown-item profile-info" href="#" >
                            <div class="d-flex justify-content-between">
                                <div class="d-flex flex-column gap" style="--gap: 2px">
                                    <span class="profile-name">${
                                      config?.profile?.name
                                    }</span>
                                    ${
                                      config?.profile?.current_role
                                        ? `<span class="profile-role">${config?.profile?.current_role}</span>`
                                        : ""
                                    }
                                   
                                </div>
                                <div style="display: none; !important">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20"
                                        fill="none">
                                        <path
                                            d="M8.15859 15.4741L13.0204 10.6123C13.0204 10.6123 13.7985 9.99906 12.9407 9.24984L8.3555 4.73424C8.16175 4.54361 7.88754 4.44284 7.62034 4.4944C7.44144 4.52877 7.26252 4.62877 7.1633 4.8694C6.91642 5.47018 7.31096 5.83112 7.31096 5.83112L11.4712 9.97712L7.31096 14.1521C7.31096 14.1521 6.84846 14.6467 7.1633 15.1271C7.47736 15.6076 8.09846 15.5349 8.15862 15.474"
                                            fill="#A3ABB1" />
                                    </svg>
                                </div>
                            </div>
                        </a>
                    </li>
                    ${
                      config?.profile?.roles?.length
                        ? `<li>
                              <hr class="profile-dropdown-divider">
                          </li>
                          <li>
                              <div class="profile-roles complete-hidden-scroll-style">
                              ${config?.profile?.roles
                                ?.map(({ url, label }) => {
                                  return `<div class="dropdown-item profile-each-role">
                                  <span class="label">${label}</span>
                              </div>`;
                                })
                                .join("")}
                              </div>
                          </li>`
                        : ""
                    }
                    
                    <li>
                        <hr class="profile-dropdown-divider">
                    </li>
                    <li ${
                      config?.display_edit_profile === false
                        ? "style=display:none"
                        : ""
                    }>
                          <button type="button" class="dropdown-item profile-menu-option" id="open-edit-drawer">
                              <span class="profile-menu-name">Edit</span>
                          </button>
                    </li>
                   
                  
                     
                    <li>
                        <hr class="profile-dropdown-divider">
                    </li>
                    <li>
                        <a class="dropdown-item profile-logout" href="/logout${config.login_url ? "?redirect_url=" + config.login_url : ""}">
                            <span class="profile-name">Log Out</span>
                        </a>
                    </li>
                </ul>
            </div>
                </div>
            </nav>
            <main class="small-device-height-fix2 d-flex flex-grow-1 overflow-y-auto">
              <div class="mobile-frame-side-navbar-modal">
                <div class="nav mobile-frame-side-navbar complete-hidden-scroll-style">
                  <button type="button" class="btn close-mobile-frame-side-navbar">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M17.1474 6.14745L12.3445 10.9505C12.1479 11.1471 11.836 11.1471 11.656 10.9505L6.85242 6.14745C6.65583 5.95085 6.34395 5.95085 6.16401 6.14745C5.96741 6.34405 5.96741 6.65593 6.16401 6.83588L10.9676 11.6396C11.1642 11.8362 11.1642 12.148 10.9676 12.328L6.14745 17.1476C5.95085 17.3442 5.95085 17.656 6.14745 17.836C6.34404 18.0326 6.65592 18.0326 6.83587 17.836L11.6395 13.0323C11.8361 12.8357 12.148 12.8357 12.3279 13.0323L17.1474 17.8526C17.344 18.0492 17.6559 18.0492 17.8358 17.8526C18.0324 17.656 18.0324 17.3441 17.8358 17.1641L13.0489 12.3439C12.8523 12.1473 12.8523 11.8354 13.0489 11.6555L17.8526 6.85178C18.0491 6.65518 18.0491 6.3433 17.8526 6.16335C17.656 5.96675 17.3447 5.96675 17.1475 6.14734L17.1474 6.14745Z" fill="black" stroke="black"/>
                    </svg>
                  </button>
                  ${config.menu
                    ?.map(({ url, icon, name, children }) => {
                      let isIconSvg = icon?.indexOf("<svg") !== -1;
                      let excatUrl =
                        url[url.length - 1] === "/" ? url : url + "/";
                      let isPathnameMatched =
                        pathname === excatUrl ||
                        (children?.length
                          ? children?.some(
                              (submenu) =>
                                (submenu?.url[submenu?.url.length - 1] === "/"
                                  ? submenu?.url
                                  : submenu?.url + "/") === pathname
                            )
                          : false);
                      if (children?.length) {
                        return ` <li>
                            <div class="dropdown mobile-frame-submenu-dropdown dropend position-relative ${
                              isPathnameMatched
                                ? "selected-each-frame-menu"
                                : ""
                            }">
                                <div class="btn w-100 position-relative d-flex align-items-center gap each-mobile-frame-link"
                                    role="button" data-bs-toggle="dropdown" aria-expanded="false" data-bs-offset="24,0"
                                    style="--bs-btn-padding-x:0px;--bs-btn-padding-y:0px;border:0px;--gap: 16px">
                                    ${
                                      icon
                                        ? isIconSvg
                                          ? icon
                                          : `<img src=${icon} alt=${name} width="40px" height="40px"/>`
                                        : `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 33 32" fill="none">
                                              <path
                                                  d="M5.61995 12.8V20.48H13.3V12.8H5.61995ZM15.22 10.88V22.4H3.69995V10.88H15.22ZM23.22 20.48C25.5175 20.48 27.38 18.6175 27.38 16.32C27.38 14.0225 25.5175 12.16 23.22 12.16C20.9224 12.16 19.06 14.0225 19.06 16.32C19.06 18.6175 20.9224 20.48 23.22 20.48ZM23.22 22.4C19.8625 22.4 17.14 19.6775 17.14 16.32C17.14 12.9625 19.8624 10.24 23.22 10.24C26.5775 10.24 29.2999 12.9625 29.2999 16.32C29.2999 19.6775 26.5775 22.4 23.22 22.4Z"
                                                  fill="var(--side-navbar-color)" />
                                          </svg>`
                                    }
                                    <span class="mobile-each-frame-menu-label">
                                        ${name}
                                    </span>
                                    <div class="mobile-frame-sidenav-menu-arrow">
                                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                        <path d="M15.9081 7.50888C15.2696 8.11715 14.6311 8.72484 13.9927 9.33305C12.9736 10.304 11.9576 11.2726 10.9385 12.2436C10.7033 12.4678 10.4687 12.6892 10.2335 12.9135C10.1146 13.0288 9.88579 13.0288 9.76689 12.9135C9.1284 12.3052 8.48991 11.6976 7.85145 11.0893C6.83231 10.1184 5.81639 9.14975 4.79729 8.17884C4.56205 7.95457 4.32748 7.73317 4.09224 7.50888C3.80079 7.23156 4.26737 6.81239 4.55883 7.09261C5.19732 7.70087 5.83581 8.30857 6.47427 8.91678C7.49341 9.8877 8.50933 10.8564 9.52843 11.8273C9.76367 12.0516 9.76476 12.0509 10 12.2752C10.6385 11.6669 11.0439 11.2813 11.6823 10.6731C12.7015 9.70215 13.7174 8.73348 14.7365 7.76257C14.9717 7.53829 15.2063 7.3169 15.4415 7.09261C15.7298 6.81528 16.1996 7.23156 15.9081 7.50888Z" fill="black" stroke="black" stroke-width="1.5"/>
                                      </svg>
                                    </div>
                                </div>

                                <ul class="dropdown-menu mobile-frame-sidenav-dropdown-menu">
                                ${children
                                  ?.map((eachSubMenu) => {
                                    let isPathname =
                                      pathname ===
                                      (eachSubMenu?.url[
                                        eachSubMenu?.url.length - 1
                                      ] === "/"
                                        ? eachSubMenu?.url
                                        : eachSubMenu?.url + "/");

                                    return `<li>
                                    <a class="dropdown-item ${
                                      isPathname
                                        ? "selected-each-frame-submenu"
                                        : ""
                                    }" href="${eachSubMenu?.url ?? "#"}">
                                        <span class="each-mobile-frame-submenu-label">${
                                          eachSubMenu?.name
                                        }</span>
                                    </a>
                                </li>`;
                                  })
                                  .join("")}
                                </ul>
                            </div>
                        </li>`;
                      } else {
                        return `<li class="nav-item ${
                          isPathnameMatched ? "selected-each-frame-menu" : ""
                        }">
                            <a class="nav-link active w-100 d-flex align-items-center gap each-mobile-frame-link"
                            style="--gap: 16px" aria-current="#asdas" href=${url}>
                            ${
                              icon
                                ? isIconSvg
                                  ? icon
                                  : `<img src=${icon} alt=${name} width="40px" height="40px"/>`
                                : `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 33 32" fill="none">
                                      <path
                                          d="M5.61995 12.8V20.48H13.3V12.8H5.61995ZM15.22 10.88V22.4H3.69995V10.88H15.22ZM23.22 20.48C25.5175 20.48 27.38 18.6175 27.38 16.32C27.38 14.0225 25.5175 12.16 23.22 12.16C20.9224 12.16 19.06 14.0225 19.06 16.32C19.06 18.6175 20.9224 20.48 23.22 20.48ZM23.22 22.4C19.8625 22.4 17.14 19.6775 17.14 16.32C17.14 12.9625 19.8624 10.24 23.22 10.24C26.5775 10.24 29.2999 12.9625 29.2999 16.32C29.2999 19.6775 26.5775 22.4 23.22 22.4Z"
                                          fill="var(--side-navbar-color)" />
                                  </svg>`
                            }
                              <span class="mobile-each-frame-menu-label">
                              ${name}
                              </span>
                            </a>
                            </li>`;
                      }
                    })
                    .join("")}
                  </div>
                </div>
                <ul class="nav frame-side-navbar complete-hidden-scroll-style">
                ${config.menu
                  ?.map(({ url, icon, name, children }) => {
                    let isIconSvg = icon?.indexOf("<svg") !== -1;
                    let excatUrl =
                      url[url.length - 1] === "/" ? url : url + "/";
                    let isPathnameMatched =
                      pathname === excatUrl ||
                      (children?.length
                        ? children?.some(
                            (submenu) =>
                              (submenu?.url[submenu?.url.length - 1] === "/"
                                ? submenu?.url
                                : submenu?.url + "/") === pathname
                          )
                        : false);
                    if (children?.length) {
                      return ` <li>
                          <div class="dropdown frame-submenu-dropdown dropend position-relative ${
                            isPathnameMatched ? "selected-each-frame-menu" : ""
                          }">
                              <div class="btn w-100 d-flex flex-column align-items-center gap each-frame-link"
                                  role="button" data-bs-toggle="dropdown" aria-expanded="false" data-bs-offset="24,0"
                                  style="--bs-btn-padding-x:0px;--bs-btn-padding-y:0px;border:0px;--gap: 4px">
                                  ${
                                    icon
                                      ? isIconSvg
                                        ? icon
                                        : `<img src=${icon} alt=${name} width="33px" height="33px"/>`
                                      : `<svg xmlns="http://www.w3.org/2000/svg" width="33" height="32" viewBox="0 0 33 32" fill="none">
                                            <path
                                                d="M5.61995 12.8V20.48H13.3V12.8H5.61995ZM15.22 10.88V22.4H3.69995V10.88H15.22ZM23.22 20.48C25.5175 20.48 27.38 18.6175 27.38 16.32C27.38 14.0225 25.5175 12.16 23.22 12.16C20.9224 12.16 19.06 14.0225 19.06 16.32C19.06 18.6175 20.9224 20.48 23.22 20.48ZM23.22 22.4C19.8625 22.4 17.14 19.6775 17.14 16.32C17.14 12.9625 19.8624 10.24 23.22 10.24C26.5775 10.24 29.2999 12.9625 29.2999 16.32C29.2999 19.6775 26.5775 22.4 23.22 22.4Z"
                                                fill="var(--side-navbar-color)" />
                                        </svg>`
                                  }
                                  <span class="each-frame-menu-label">
                                      ${name}
                                  </span>
                                  <div class="frame-sidenav-menu-arrow">
                                      <svg xmlns="http://www.w3.org/2000/svg" width="6" height="6" viewBox="0 0 6 6" fill="none">
                                          <g clip-path="url(#clip0_5530_3090)">
                                              <path
                                                  d="M5.99999 5.24758V0.747281C5.99999 -0.127468 5.44766 -0.206217 4.87705 0.364756L0.371255 4.86649C-0.285163 5.52279 -0.0136801 6 0.736506 6H5.23762C5.65209 6 6 5.66248 6 5.24761L5.99999 5.24758Z"
                                                  fill="var(--side-navbar-color)" />
                                          </g>
                                          <defs>
                                              <clipPath id="clip0_5530_3090">
                                                  <rect width="6" height="6" fill="white" />
                                              </clipPath>
                                          </defs>
                                      </svg>
                                  </div>
                              </div>

                              <ul class="dropdown-menu frame-sidenav-dropdown-menu">
                              ${children
                                ?.map((eachSubMenu) => {
                                  let isPathname =
                                    pathname ===
                                    (eachSubMenu?.url[
                                      eachSubMenu?.url.length - 1
                                    ] === "/"
                                      ? eachSubMenu?.url
                                      : eachSubMenu?.url + "/");

                                  return `<li>
                                  <a class="dropdown-item ${
                                    isPathname
                                      ? "selected-each-frame-submenu"
                                      : ""
                                  }" href="${eachSubMenu?.url ?? "#"}">
                                      <span class="each-frame-submenu-label">${
                                        eachSubMenu?.name
                                      }</span>
                                  </a>
                              </li>`;
                                })
                                .join("")}
                              </ul>
                          </div>
                      </li>`;
                    } else {
                      return `<li class="nav-item ${
                        isPathnameMatched ? "selected-each-frame-menu" : ""
                      }">
                          <a class="nav-link active w-100 d-flex flex-column align-items-center gap each-frame-link"
                          style="--gap: 4px" aria-current="#asdas" href=${url}>
                          ${
                            icon
                              ? isIconSvg
                                ? icon
                                : `<img src=${icon} alt=${name} width="33px" height="33px"/>`
                              : `<svg xmlns="http://www.w3.org/2000/svg" width="33" height="32" viewBox="0 0 33 32" fill="none">
                                    <path
                                        d="M5.61995 12.8V20.48H13.3V12.8H5.61995ZM15.22 10.88V22.4H3.69995V10.88H15.22ZM23.22 20.48C25.5175 20.48 27.38 18.6175 27.38 16.32C27.38 14.0225 25.5175 12.16 23.22 12.16C20.9224 12.16 19.06 14.0225 19.06 16.32C19.06 18.6175 20.9224 20.48 23.22 20.48ZM23.22 22.4C19.8625 22.4 17.14 19.6775 17.14 16.32C17.14 12.9625 19.8624 10.24 23.22 10.24C26.5775 10.24 29.2999 12.9625 29.2999 16.32C29.2999 19.6775 26.5775 22.4 23.22 22.4Z"
                                        fill="var(--side-navbar-color)" />
                                </svg>`
                          }
                            <span class="each-frame-menu-label">
                            ${name}
                            </span>
                          </a>
                          </li>`;
                    }
                  })
                  .join("")}
                </ul>
                <div class="d-flex flex-grow-1 frame-page">
                    <slot name="frame-page">
                    </slot>
                </div>
            </main>
            <div>
            <div id="drawer-backdrop" class="drawer-backdrop"></div>
            <div id="sideDrawer" class="sideDrawerContainer">
              <button type="button" class="closebtn" id="close-drawer">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <g clip-path="url(#clip0_5600_3662)">
                  <path d="M17.7213 1.22117L10.5168 8.42571C10.2219 8.72061 9.75409 8.72061 9.48417 8.42571L2.27865 1.22117C1.98375 0.926275 1.51593 0.926275 1.24601 1.22117C0.951112 1.51607 0.951112 1.9839 1.24601 2.25382L8.45153 9.45933C8.74643 9.75423 8.74643 10.2221 8.45153 10.492L1.22117 17.7213C0.926275 18.0162 0.926275 18.4841 1.22117 18.754C1.51607 19.0489 1.9839 19.0489 2.25382 18.754L9.45933 11.5485C9.75423 11.2536 10.2221 11.2536 10.492 11.5485L17.7213 18.7788C18.0162 19.0737 18.4841 19.0737 18.754 18.7788C19.0489 18.4839 19.0489 18.0161 18.754 17.7462L11.5736 10.5158C11.2787 10.2209 11.2787 9.7531 11.5736 9.48319L18.7791 2.27767C19.074 1.98277 19.074 1.51494 18.7791 1.24503C18.4842 0.950129 18.0173 0.950129 17.7214 1.22101L17.7213 1.22117Z" fill="black" stroke="black" stroke-width="0.4"/>
                </g>
                <defs>
                  <clipPath id="clip0_5600_3662">
                    <rect width="20" height="20" fill="white"/>
                  </clipPath>
                </defs>
                </svg>
              </button>
              <div class="content-container">
                  <div id="profile-drawer-header" id="redirect-to-change-password" class="drawer-header">
                    Change password
                  </div>
                  <div class="server-drawer-error" id="drawer-server-error">
                
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                        <path d="M17.0609 5.5983C16.6196 4.55669 15.9871 3.62128 15.1843 2.81633C14.38 2.01348 13.4445 1.38168 12.4023 0.939756C11.3237 0.48248 10.1788 0.25 8.99893 0.25C4.17489 0.251396 0.25 4.17704 0.25 9.00107C0.25 13.8251 4.17489 17.75 8.99893 17.75C13.823 17.75 17.7479 13.8251 17.7479 9.00107C17.7479 7.82123 17.5175 6.67627 17.0602 5.59769L17.0609 5.5983ZM8.99893 16.304C4.97216 16.304 1.69657 13.0284 1.69657 9.00168C1.69657 4.97492 4.97216 1.69932 8.99893 1.69932C13.0257 1.69932 16.3013 4.97492 16.3013 9.00168C16.3013 13.0284 13.0257 16.304 8.99893 16.304Z" fill="#FBE0DD"/>
                        <path d="M11.3103 7.54624C11.5504 7.3064 11.565 6.93203 11.3402 6.69279C11.1001 6.43833 10.7107 6.43833 10.4706 6.67758L9.40599 7.74104C9.18112 7.96567 8.82158 7.96567 8.59672 7.74104L7.54735 6.69279C7.30726 6.45295 6.93249 6.43834 6.69299 6.66296C6.43827 6.9028 6.43827 7.29179 6.67777 7.53163L7.74236 8.59509C7.96723 8.81972 7.96723 9.17888 7.74236 9.4035L6.693 10.4518C6.4529 10.6916 6.43827 11.0958 6.693 11.335C6.81304 11.4397 6.96295 11.5 7.11286 11.5C7.26277 11.5 7.42791 11.4403 7.53273 11.3204L8.59732 10.257C8.82219 10.0323 9.18173 10.0323 9.40659 10.257L10.4712 11.3204C10.5912 11.4403 10.7411 11.5 10.8911 11.5C11.041 11.5 11.1909 11.4403 11.3109 11.335C11.5656 11.0952 11.551 10.691 11.3109 10.4518L10.2616 9.4035C10.0367 9.17888 10.0367 8.81972 10.2616 8.59509L11.3103 7.54624Z" fill="#FBE0DD"/>
                        </svg>
                    
                 
                      <div id="drawer-server-error-text">
                        server error
                      </div>
                    
                  </div>
                  <form id="drawer-form" action="">
                    <div id="drawer-content" class="drawer-content">
                    
                    
                      
                    </div>

                    <div class="drawer-submit">
                    <button id="submitPasswordChange" type="submit" class="submit-button">
                      Update password
                    </button>
                    </div>
                  </form>
              </div>
            </div>
            </div>

            <div class="profileDrawerContainer" tabindex="-1" id="user-profile-drawer">

              <button type="button" class="btn-close" id="close-user-profile-drawer">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <g clip-path="url(#clip0_2403_2581)">
                    <path d="M17.7213 1.22117L10.5168 8.42571C10.2219 8.72061 9.75409 8.72061 9.48417 8.42571L2.27865 1.22117C1.98375 0.926275 1.51593 0.926275 1.24601 1.22117C0.951112 1.51607 0.951112 1.9839 1.24601 2.25382L8.45153 9.45933C8.74643 9.75423 8.74643 10.2221 8.45153 10.492L1.22117 17.7213C0.926275 18.0162 0.926275 18.4841 1.22117 18.754C1.51607 19.0489 1.9839 19.0489 2.25382 18.754L9.45933 11.5485C9.75423 11.2536 10.2221 11.2536 10.492 11.5485L17.7213 18.7788C18.0162 19.0737 18.4841 19.0737 18.754 18.7788C19.0489 18.4839 19.0489 18.0161 18.754 17.7462L11.5736 10.5158C11.2787 10.2209 11.2787 9.7531 11.5736 9.48319L18.7791 2.27767C19.074 1.98277 19.074 1.51494 18.7791 1.24503C18.4842 0.950129 18.0173 0.950129 17.7214 1.22101L17.7213 1.22117Z" fill="black" stroke="black" stroke-width="0.4"/>
                  </g>
                  <defs>
                    <clipPath id="clip0_2403_2581">
                      <rect width="20" height="20" fill="white"/>
                    </clipPath>
                  </defs>
                </svg>
              </button>

              <div class="profile-drawer-container">
                <div class="profile-left-side">
                    <div class="profile-drawer-title">
                        PROFILE
                    </div>
                    <div class="profile-name-container">
                        <div>
                            <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M120 60C120 70.9524 117.066 81.2227 111.931 90.0644C111.736 90.399 111.532 90.7336 111.326 91.0682C110.848 91.8661 110.348 92.6641 109.82 93.4363C109.601 93.7581 109.382 94.0798 109.136 94.4016C101.313 105.611 89.7297 113.977 76.242 117.773C75.9588 117.851 75.6628 117.928 75.3784 118.005C70.4762 119.305 65.3153 120 60 120C39.2664 120 20.9768 109.485 10.2317 93.4878C9.21493 92.0077 8.27542 90.4633 7.41312 88.8932C2.68854 80.3218 0 70.4762 0 60C0 26.8597 26.8597 7.62939e-06 60 7.62939e-06C93.1403 7.62939e-06 120 26.8597 120 60Z"
                                    fill="#DDE2E5" />
                                <g clip-path="url(#clip0_3621_4064)">
                                    <path
                                        d="M60 0C26.9065 0 0 26.9065 0 60C0 93.0935 26.9065 120 60 120C93.0935 120 120 93.0935 120 60C120 26.9065 93.0935 0 60 0ZM60 34.3566C70.3569 34.3566 78.8185 42.8188 78.8185 53.1752C78.8185 63.532 70.3564 71.9937 60 71.9937C49.6436 71.9937 41.1815 63.5315 41.1815 53.1752C41.1815 42.8183 49.6436 34.3566 60 34.3566ZM27.1579 96.3802V93.6023C27.1579 85.6434 33.602 79.076 41.6842 79.076H78.3158C86.2747 79.076 92.8421 85.5201 92.8421 93.6023V96.3802C84.1283 104.211 72.6316 109.012 60 109.012C47.3684 109.012 35.8712 104.211 27.1579 96.3802Z"
                                        fill="#F0F3F4" />
                                </g>
                                <defs>
                                    <clipPath id="clip0_3621_4064">
                                        <rect width="120" height="120" fill="white" />
                                    </clipPath>
                                </defs>
                            </svg>
                        </div>
                        <div class="profile-name-change-password-container">
                            <div class="user-name">${config?.profile?.name}</div>
                        ${
                          config?.allow_change_password
                            ? `
                            <div class="change-password-btn" id="open-password-drawer">Change Password</div>
                            `
                            : ""
                        }
                        </div>
                    </div>
                    <div class="profile-detail-container">

                        <div class="profile-detail-individual-data-container">
                            <div class="profile-detail-individual-label">
                                <div class="profile-detail-individual-label-text">
                                    User role:</div>
                            </div>
                            <div class="profile-detail-individual-label-data-container">
                                ${config?.profile?.current_role}
                            </div>
                        </div>

                        ${
                          config?.profile?.email
                            ? `<div class="profile-detail-individual-data-container">
                            <div class="profile-detail-individual-label">
                                <div class="profile-detail-individual-label-text">
                                    Email:</div>
                            </div>
                            <div class="profile-detail-individual-label-data-container">
                                ${config?.profile?.email}
                            </div>
                        </div>`
                            : ""
                        }

                        ${
                          config?.profile?.mobile_number
                            ? `<div class="profile-detail-individual-data-container">
                            <div class="profile-detail-individual-label">
                                <div class="profile-detail-individual-label-text">
                                    Mobile number:</div>
                            </div>
                            <div class="profile-detail-individual-label-data-container">
                                ${config?.profile?.mobile_number}
                            </div>
                        </div>`
                            : ""
                        }

                        ${
                          config?.profile?.other_roles.length > 0
                            ? `<div class="profile-detail-individual-data-container">
                            <div class="profile-detail-individual-label">
                                <div class="profile-detail-individual-label-text">
                                    Other roles:</div>
                            </div>
                            <div class="profile-detail-individual-label-data-container">
                                ${config?.profile?.other_roles?.map((el) => {
                                  return `<div>${el?.label}</div>`;
                                })}
                            </div>
                        </div>`
                            : ""
                        }

                        ${
                          config?.profile?.date_of_registration
                            ? `<div class="profile-detail-individual-data-container">
                            <div class="profile-detail-individual-label">
                                <div class="profile-detail-individual-label-text">
                                    Date of registration:</div>
                            </div>
                            <div class="profile-detail-individual-label-data-container">
                                ${config?.profile?.date_of_registration}
                            </div>
                        </div>`
                            : ""
                        }

                        ${
                          config?.profile?.last_login
                            ? `<div class="profile-detail-individual-data-container">
                            <div class="profile-detail-individual-label">
                                <div class="profile-detail-individual-label-text">
                                    Last login date:</div>
                            </div>
                            <div class="profile-detail-individual-label-data-container">
                                ${config?.profile?.last_login}
                            </div>
                        </div>`
                            : ""
                        }

                    </div>
                
                </div>
               
            </div>
             
            </div>
        </div>`;

    this.shadowRoot.appendChild(template.content.cloneNode(true));

    let shadowRoot = this.shadowRoot;

    shadowRoot
      .querySelector(".mobile-frame-side-navbar-modal")
      .addEventListener("click", function (event) {
        event.stopImmediatePropagation();
        const hasClass = event.target.classList.contains(
          "mobile-frame-side-navbar"
        );
        if (!hasClass) {
          shadowRoot
            .querySelector(".mobile-frame-side-navbar-modal")
            .classList.remove("open");
        }
      });

    shadowRoot
      .querySelector(".open-mobile-frame-side-navbar")
      .addEventListener("click", function (event) {
        event.stopImmediatePropagation();
        shadowRoot
          .querySelector(".mobile-frame-side-navbar-modal")
          .classList.add("open");
      });

    shadowRoot
      .querySelector(".close-mobile-frame-side-navbar")
      .addEventListener("click", function (event) {
        event.stopImmediatePropagation();
        shadowRoot
          .querySelector(".mobile-frame-side-navbar-modal")
          .classList.remove("open");
      });

    // Side Navbar Events
    shadowRoot
      .querySelectorAll(".frame-submenu-dropdown")
      .forEach(function (frameSubMenuItem) {
        const subMenuDropdownElement = frameSubMenuItem;

        const button = frameSubMenuItem.querySelector(".each-frame-link");
        const tooltip = frameSubMenuItem.querySelector(".dropdown-menu");

        const popperInstance = Popper.createPopper(button, tooltip, {
          strategy: "fixed",
          modifiers: [
            {
              name: "offset",
              options: {
                offset: [30, 0],
              },
            },
          ],
        });
        popperInstance.setOptions({ placement: "right-start" });

        subMenuDropdownElement.addEventListener("click", function (event) {
          event.stopImmediatePropagation();
          shadowRoot
            .querySelectorAll(".dropdown-menu")
            .forEach(function (each) {
              each.style.display = "none";
            });
          shadowRoot
            .querySelectorAll(".frame-submenu-dropdown")
            .forEach(function (each) {
              each.classList.remove("focused-frame-parent-menu");
            });
          this.classList.add("focused-frame-parent-menu");
          this.querySelector(".dropdown-menu").style.display = "flex";
          popperInstance.update();
        });

        document.addEventListener("click", function (event) {
          const isClickInside = subMenuDropdownElement.contains(event.target);
          if (!isClickInside) {
            subMenuDropdownElement.querySelector(
              ".dropdown-menu"
            ).style.display = "none";
          }
        });
      });

    // Side Navbar Events
    shadowRoot
      .querySelectorAll(".mobile-frame-submenu-dropdown")
      .forEach(function (frameSubMenuItem) {
        const subMenuDropdownElement = frameSubMenuItem;

        subMenuDropdownElement.addEventListener("click", function (event) {
          event.stopImmediatePropagation();
          let isDisplayed =
            this.querySelector(".dropdown-menu")?.style?.display === "flex";
          if (!isDisplayed) {
            shadowRoot
              .querySelectorAll(".mobile-frame-sidenav-menu-arrow")
              .forEach(function (each) {
                each.classList.remove("rotate-arrow");
              });
            shadowRoot
              .querySelectorAll(".dropdown-menu")
              .forEach(function (each) {
                each.style.display = "none";
              });
            shadowRoot
              .querySelectorAll(".mobile-frame-submenu-dropdown")
              .forEach(function (each) {
                each.classList.remove("focused-frame-parent-menu");
              });
            this.classList.add("focused-frame-parent-menu");
            this.querySelector(
              ".mobile-frame-sidenav-menu-arrow"
            ).classList.add("rotate-arrow");
            this.querySelector(".dropdown-menu").style.display = "flex";
          } else {
            subMenuDropdownElement
              .querySelector(".mobile-frame-sidenav-menu-arrow")
              .classList.remove("rotate-arrow");
            subMenuDropdownElement.querySelector(
              ".dropdown-menu"
            ).style.display = "none";
          }
        });

        document.addEventListener("click", function (event) {
          const isClickInside = subMenuDropdownElement.contains(event.target);
          if (!isClickInside) {
            subMenuDropdownElement
              .querySelector(".mobile-frame-sidenav-menu-arrow")
              .classList.remove("rotate-arrow");
            subMenuDropdownElement.querySelector(
              ".dropdown-menu"
            ).style.display = "none";
          }
        });
      });

    // Profile Events
    const button = shadowRoot.querySelector(".profile-dropdown-menu-button");
    const tooltip = shadowRoot.querySelector(".profile-dropdown-menu");

    const profilePopperInstance = Popper.createPopper(button, tooltip, {
      modifiers: [
        {
          name: "offset",
          options: {
            offset: [0, 10],
          },
        },
      ],
    });
    profilePopperInstance.setOptions({ placement: "bottom-end" });

    const profileDropdownElement = shadowRoot.querySelector(".dropdown");

    profileDropdownElement.addEventListener("click", function (event) {
      event.stopImmediatePropagation();
      shadowRoot.querySelectorAll(".dropdown-menu").forEach(function (each) {
        each.style.display = "none";
      });
      this.querySelector(".dropdown-menu").style.display = "block";
      profilePopperInstance.update();
    });

    document.addEventListener("click", function (event) {
      const isClickInside = profileDropdownElement.contains(event.target);
      if (!isClickInside) {
        profileDropdownElement.querySelector(".dropdown-menu").style.display =
          "none";
      }
    });

    document.body.click();
    let profileData;


    shadowRoot.querySelector("#profile-info").addEventListener("click", function () {
      var w = window.innerWidth;
      // shadowRoot.querySelector("#user-profile-drawer").style.width = "calc(100% - 88px)";
      if (w < 641) {
        shadowRoot.querySelector("#user-profile-drawer").style.width =
          "calc(100%)";
      } else {
        shadowRoot.querySelector("#user-profile-drawer").style.width = "calc(100% - 88px)";
      }
      
    });

    shadowRoot
      .querySelector("#close-user-profile-drawer")
      .addEventListener("click", function () {
        shadowRoot.querySelector("#user-profile-drawer").style.width = "0px";
      });

    shadowRoot
      .querySelector("#open-edit-drawer")
      .addEventListener("click", function () {
        shadowRoot.querySelector("#sideDrawer").style.width = "100%";
        shadowRoot.querySelector("#sideDrawer").style.maxWidth = "498px";
        shadowRoot.querySelector("#drawer-backdrop").style.display = "block";
        shadowRoot.getElementById("profile-drawer-header").innerHTML = `Edit`;
        shadowRoot.getElementById("submitPasswordChange").innerHTML = `Save`;
        drawerType = "Edit";
        shadowRoot.getElementById("submitPasswordChange").style.opacity = "1";

        shadowRoot.getElementById("drawer-content").innerHTML = `
                      <div class="form-field-container">
                        <label class="form-label" for="name">
                          Name
                        </label>
                        <input placeholder="Enter name" required id="name" type="text" class="drawer-input" />
                        <div class="drawer-error" id="edit-name-error">Please enter valid name</div>
                      </div>

                      <div class="form-field-container">
                        <label class="form-label" for="mobile">
                        Mobile
                        </label>
                        <input placeholder="Enter mobile"  id="mobile" type="text" class="drawer-input" />
                        <div class="drawer-error"  id="edit-mobile-error">Please enter valid mobile</div>
                      </div>

                      <div class="form-field-container">
                        <label class="form-label" for="email">
                          Email
                        </label>
                        <input placeholder="Enter email"  id="email" type="email" class="drawer-input" />
                        <div class="drawer-error"  id="edit-email-error">Please enter valid email</div>
                        <div class="drawer-error"  id="enter-either-email-mobile-error">You must enter either a mobile number or an email.</div>
                      </div>
             
              `;
        
        fetch(baseUrl)
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          })
          .then(data => {
            profileData = data.response.profile_data;
            shadowRoot.getElementById("name").value =
              data.response.profile_data?.name;
            shadowRoot.getElementById("mobile").value =
              data.response.profile_data?.mobile;
            shadowRoot.getElementById("email").value =
              data.response.profile_data?.email;
          })
          .catch(error => {
            console.error('Fetch error:', error);
          });
      });
    
    let openPasswordDrawerElement = shadowRoot.querySelector("#open-password-drawer");
    if(openPasswordDrawerElement){
      openPasswordDrawerElement
        .addEventListener("click", function () {
          shadowRoot.querySelector("#sideDrawer").style.width = "100%";
          shadowRoot.querySelector("#sideDrawer").style.maxWidth = "498px";
          shadowRoot.querySelector("#drawer-backdrop").style.display = "block";
          shadowRoot.getElementById(
            "profile-drawer-header"
          ).innerHTML = `Change password`;
          shadowRoot.getElementById(
            "submitPasswordChange"
          ).innerHTML = `Update password`;
          drawerType = "change password";
          shadowRoot.getElementById("submitPasswordChange").style.opacity = "1";

          shadowRoot.getElementById("drawer-content").innerHTML = `
                      <div class="form-field-container">
                        <label class="form-label" for="currentPassword">
                          Current password
                        </label>
                        <input placeholder="Current password" required id="currentPassword" type="password" class="drawer-input" />
                      </div>

                      <div class="form-field-container">
                        <label class="form-label" for="newPassword">
                        New password
                        </label>
                        <input placeholder="New password" required id="newPassword" type="password" class="drawer-input" />
                        <div class="drawer-error"  id="new-password-error">Password must be at least 8 characters long, with lower and upper case letters, numbers and symbols.</div>
                      </div>

                      <div class="form-field-container">
                        <label class="form-label" for="confirmPassword">
                          Confirm password
                        </label>
                        <input placeholder="Confirm password" required id="confirmPassword" type="password" class="drawer-input" />
                        <div class="drawer-error"  id="edit-confirmPassword-error">Both password doesn't match</div>
                      </div>

              `;
        });
    }

    shadowRoot
      .querySelector("#drawer-form")
      .addEventListener("change", function () {
        if (drawerType === "Change Password") {
          if (
            shadowRoot.getElementById("currentPassword").value != "" &&
            shadowRoot.getElementById("newPassword").value != "" &&
            shadowRoot.getElementById("confirmPassword").value != ""
          ) {
            shadowRoot.getElementById("submitPasswordChange").style.opacity =
              "1";
          }
        }
      });

    shadowRoot
      .querySelector("#submitPasswordChange")
      .addEventListener("click", function (event) {
        event.stopImmediatePropagation();

        if (drawerType === "change password") {
          let passwordPattern =
            /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
          if (
            !passwordPattern.test(
              shadowRoot.getElementById("newPassword").value
            )
          ) {
            shadowRoot.querySelector("#new-password-error").style.display =
              "block";
            return;
          } else {
            shadowRoot.querySelector("#new-password-error").style.display =
              "none";
          }

          if (
            passwordPattern.test(
              shadowRoot.getElementById("newPassword").value
            ) &&
            shadowRoot.getElementById("newPassword").value !==
              shadowRoot.getElementById("confirmPassword").value
          ) {
            shadowRoot.querySelector(
              "#edit-confirmPassword-error"
            ).style.display = "block";
            return;
          }

          let postData = new FormData();

          postData.append(
            "current_password",
            shadowRoot.getElementById("currentPassword").value
          );
          postData.append(
            "new_password",
            shadowRoot.getElementById("newPassword").value
          );

          let csrfToken = getCookie("csrftoken");

          fetch("/api/v1/profile/change_password/", {
            method: "PUT",
            body: postData,
            headers: {
              "X-CSRFTOKEN": csrfToken,
            },
          })
            .then(function (response) {
              return response.json();
            })
            .then(function (data) {
              if (data.success) {
                shadowRoot.querySelector("#sideDrawer").style.width = "0px";
                shadowRoot.querySelector("#drawer-backdrop").style.display =
                  "none";
              } else {
                shadowRoot.getElementById("drawer-server-error").style.display =
                  "flex";
                shadowRoot.getElementById(
                  "drawer-server-error-text"
                ).innerHTML = data.response?.message;
              }
            })
            .catch(function (error) {
              console.error("Error:", error);
            });
        } else {
          let regex =
            /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

          if (shadowRoot.getElementById("name").value == "") {
            shadowRoot.getElementById("edit-name-error").style.display =
              "block";
            return;
          } else {
            shadowRoot.getElementById("edit-name-error").style.display = "none";
          }

          if (
            shadowRoot.getElementById("mobile").value == "" &&
            shadowRoot.getElementById("email").value == ""
          ) {
            shadowRoot.getElementById(
              "enter-either-email-mobile-error"
            ).style.display = "block";
            return;
          } else {
            shadowRoot.getElementById(
              "enter-either-email-mobile-error"
            ).style.display = "none";
          }

          if (
            profileData.mobile !== "" &&
            shadowRoot.getElementById("mobile").value === ""
          ) {
            shadowRoot.getElementById("edit-mobile-error").style.display =
              "block";
            return;
          } else {
            shadowRoot.getElementById("edit-mobile-error").style.display =
              "none";
          }

          if (
            profileData.email !== "" &&
            shadowRoot.getElementById("email").value === ""
          ) {
            if (!regex.test(shadowRoot.getElementById("email").value)) {
              shadowRoot.getElementById("edit-email-error").style.display =
                "block";
              return;
            } else {
              shadowRoot.getElementById("edit-email-error").style.display =
                "none";
            }

            return;
          }

          let postData = new FormData();

          postData.append("name", shadowRoot.getElementById("name").value);
          postData.append("mobile", shadowRoot.getElementById("mobile").value);
          postData.append("email", shadowRoot.getElementById("email").value);

          let csrfToken = getCookie("csrftoken");

          fetch(baseUrl, {
            method: "PUT",
            body: postData,
            headers: {
              "X-CSRFTOKEN": csrfToken,
            },
          })
            .then(function (response) {
              return response.json();
            })
            .then(function (data) {
              if (data.success) {
                shadowRoot.querySelector("#sideDrawer").style.width = "0px";
                shadowRoot.querySelector("#drawer-backdrop").style.display =
                  "none";
              } else {
                shadowRoot.getElementById("drawer-server-error").style.display =
                  "flex";
                shadowRoot.getElementById(
                  "drawer-server-error-text"
                ).innerHTML = data.response?.message;
              }
            })
            .catch(function (error) {
              console.error("Error:", error);
            });
        }
      });

    shadowRoot
      .querySelector("#close-drawer")
      .addEventListener("click", function () {
        shadowRoot.getElementById("drawer-server-error").style.display = "none";
        shadowRoot.querySelector("#sideDrawer").style.width = "0px";
        shadowRoot.querySelector("#drawer-backdrop").style.display = "none";
      });
  }
}

customElements.define("z-frame", Frame);
