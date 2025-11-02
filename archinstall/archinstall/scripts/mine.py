from pathlib import Path

from archinstall.default_profiles.desktops.hyprland import HyprlandProfile
from archinstall.lib.applications.application_handler import application_handler
from archinstall.lib.args import arch_config_handler
from archinstall.lib.authentication.authentication_handler import auth_handler
from archinstall.lib.configuration import ConfigurationOutput
from archinstall.lib.disk.disk_menu import DiskLayoutConfigurationMenu
from archinstall.lib.disk.filesystem import FilesystemHandler
from archinstall.lib.global_menu import GlobalMenu
from archinstall.lib.installer import (
    Installer,
)
from archinstall.lib.models import Bootloader
from archinstall.lib.models.application import (
    ApplicationConfiguration,
    Audio,
    AudioConfiguration,
    BluetoothConfiguration,
)
from archinstall.lib.models.authentication import AuthenticationConfiguration
from archinstall.lib.models.mirrors import MirrorConfiguration, MirrorRegion
from archinstall.lib.models.network import NetworkConfiguration, NicType
from archinstall.lib.models.packages import Repository
from archinstall.lib.models.profile import ProfileConfiguration
from archinstall.lib.models.users import Password, User
from archinstall.lib.output import debug, error, info
from archinstall.lib.packages.packages import check_package_upgrade
from archinstall.lib.profile.profiles_handler import profile_handler
from archinstall.lib.translationhandler import tr
from archinstall.tui import Tui


def ask_user_questions() -> None:
    """
    First, we'll ask the user for a bunch of user input.
    Not until we're satisfied with what we want to install
    will we continue with the actual installation steps.
    """

    title_text = None

    upgrade = check_package_upgrade("archinstall")
    if upgrade:
        text = tr("New version available") + f": {upgrade}"
        title_text = f"  ({text})"

    with Tui():
        global_menu = GlobalMenu(arch_config_handler.config)

        if not arch_config_handler.args.advanced:
            global_menu.set_enabled("parallel_downloads", False)

        global_menu.run(additional_title=title_text)


def perform_installation(mountpoint: Path) -> None:
    """
    Performs the installation steps on a block device.
    Only requirement is that the block devices are
    formatted and setup prior to entering this function.
    """
    info("Starting installation...")

    config = arch_config_handler.config

    if not config.disk_config:
        error("No disk configuration provided")
        return

    disk_config = config.disk_config
    run_mkinitcpio = not config.uki
    locale_config = config.locale_config
    optional_repositories = (
        config.mirror_config.optional_repositories if config.mirror_config else []
    )
    mountpoint = disk_config.mountpoint if disk_config.mountpoint else mountpoint

    mirrors = MirrorConfiguration(
        mirror_regions=[MirrorRegion(name="", urls=[])],
        custom_servers=[],
        optional_repositories=[Repository.Multilib],
        custom_repositories=[],
    )
    hostname = "yulia"
    user = User(
        "nick",
        Password("test"),
        True,
        [
            "wheel",
            "power",
            "input",
            "audio",
            "video",
            "network",
            "storage",
            "rfkill",
            "log",
            "games",
            "gamemode",
        ],
    )
    auth_config = AuthenticationConfiguration(Password("test"))
    network_config = NetworkConfiguration(NicType.NM, nics=[])
    audio_config = AudioConfiguration(audio=Audio.PIPEWIRE)
    bluetooth_config = BluetoothConfiguration(True)
    profile_config = ProfileConfiguration(HyprlandProfile())
    packages = [
        "accountsservice",
        "fuzzel",
        "gnome-keyring",
        "hypridle",
        "hyprland",
        "hyprlock",
        "hyprpicker",
        "hyprpolkitagent",
        "hyprshot",
        "kvantum",
        "libgnome-keyring",
        "mako",
        "nwg-clipman",
        "satty",
        "swayosd",
        "swww",
        "uwsm",
        "waybar",
        "wl-clipboard",
        "xdg-desktop-portal-gtk",
        "xdg-desktop-portal-hyprland",
    ]

    timezone = "US/Eastern"
    services = []
    bootloader = Bootloader.Systemd

    with Installer(
        mountpoint,
        disk_config,
        base_packages=["base", "base-devel", "linux-firmware", "git", "nvim"],
        kernels=["linux"],
    ) as installation:
        # Mount all the drives to the desired mountpoint
        installation.mount_ordered_layout()

        installation.sanity_check()

        installation.set_mirrors(mirrors, on_target=False)

        installation.minimal_installation(
            optional_repositories=optional_repositories,
            mkinitcpio=run_mkinitcpio,
            hostname=arch_config_handler.config.hostname,
            locale_config=locale_config,
        )

        installation.set_mirrors(mirrors, on_target=True)

        installation.setup_swap("zram")

        installation.add_bootloader(bootloader, False)

        network_config.install_network_config(
            installation,
            config.profile_config,
        )

        installation.create_users(user)

        auth_handler.setup_auth(installation, auth_config, hostname)

        application_handler.install_applications(
            installation,
            ApplicationConfiguration(bluetooth_config, audio_config),
            [user],
        )

        profile_handler.install_profile_config(installation, profile_config)

        installation.add_additional_packages(packages)

        installation.set_timezone(timezone)

        installation.activate_time_synchronization()

        root_user = User("root", Password(plaintext="test"), False)
        installation.set_user_password(root_user)

        installation.enable_service(services)

        installation.genfstab()


def guided() -> None:
    with Tui():
        disk_config = DiskLayoutConfigurationMenu(disk_layout_config=None).run()
        arch_config_handler.config.disk_config = disk_config

    config = ConfigurationOutput(arch_config_handler.config)
    config.write_debug()
    config.save()

    if not arch_config_handler.args.silent:
        aborted = False
        with Tui():
            if not config.confirm_config():
                debug("Installation aborted")
                aborted = True

        if aborted:
            return guided()

    if arch_config_handler.config.disk_config:
        fs_handler = FilesystemHandler(arch_config_handler.config.disk_config)
        fs_handler.perform_filesystem_operations()

    perform_installation(arch_config_handler.args.mountpoint)


guided()
