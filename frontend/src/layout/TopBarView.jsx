import "./TopBarView.css"
import logo from "../assets/LogoWhite.png"
function TopBarView({onSettingsClick}) {
    return (
        <header className="topbar">
        <div className="topbar__section topbar__left">
            <img
                    src={logo}
                alt="Logo"
                className="topbar__logo"
                width={56}
                height={120}
                loading="eager"
                decoding="async"
            />
        </div>
        
      <h1 className="topbar__title" title="TD Generator">
        Technical Documentation Generator
      </h1>

        
      <div className="topbar__section topbar__right">
        <button

                    className="topbar__btn"
          aria-label="Einstellungen �ffnen"
          onClick={onSettingsClick}
                >

                </button>
            </div>

                </header>
    );
}

export default TopBarView;