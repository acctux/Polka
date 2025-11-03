from pathlib import Path

from archinstall.default_profiles.minimal import MinimalProfile
from archinstall.default_profiles.profile import GreeterType
from archinstall.lib.applications.application_handler import application_handler
from archinstall.lib.args import arch_config_handler
from archinstall.lib.authentication.authentication_handler import auth_handler
from archinstall.lib.configuration import ConfigurationOutput
from archinstall.lib.disk.disk_menu import DiskLayoutConfigurationMenu
from archinstall.lib.disk.filesystem import FilesystemHandler
from archinstall.lib.hardware import GfxDriver, SysInfo
from archinstall.lib.installer import Installer, run_custom_user_commands
from archinstall.lib.models.application import (
    ApplicationConfiguration,
    Audio,
    AudioConfiguration,
    BluetoothConfiguration,
)
from archinstall.lib.models.authentication import AuthenticationConfiguration
from archinstall.lib.models.bootloader import Bootloader
from archinstall.lib.models.device import (
    DiskLayoutConfiguration,
    DiskLayoutType,
    EncryptionType,
)
from archinstall.lib.models.locale import LocaleConfiguration
from archinstall.lib.models.mirrors import MirrorConfiguration, MirrorRegion
from archinstall.lib.models.network import NetworkConfiguration, NicType
from archinstall.lib.models.packages import Repository
from archinstall.lib.models.profile import ProfileConfiguration
from archinstall.lib.models.users import Password, User
from archinstall.lib.output import debug, error, info
from archinstall.lib.profile.profiles_handler import profile_handler
from archinstall.lib.translationhandler import translation_handler
from archinstall.tui.curses_menu import Tui

base_packages = ["base", "base-devel", "linux", "linux-firmware"]
my_version = "archinstall"
# app_config
bluetooth_enable = True
audio_config = Audio.PIPEWIRE
# auth_config
my_root_password = "test"
my_username = "nick"
my_password = "test"
my_sudo = True
my_groups = [
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
    # "gamemode",
]
my_kb_layout = "us"
my_sys_lang = "en_US"
my_sys_enc = "UTF-8"
arch_inst_lang = "en"
config_type = DiskLayoutType.Default
device_modifications = ([],)
lvm_config = None
mountpoint = None
my_profile = MinimalProfile()
my_gfx_driver = GfxDriver.AmdOpenSource
my_greeter = GreeterType.Lightdm
my_country_name = "United States"
my_country_urls = [
    "https://mirrors.xtom.com/archlinux/$repo/os/$arch",
    "http://mirrors.acm.wpi.edu/archlinux/$repo/os/$arch",
    "http://mirror.adectra.com/archlinux/$repo/os/$arch",
    "https://mirror.adectra.com/archlinux/$repo/os/$arch",
    "https://mirror.akane.network/archmirror/$repo/os/$arch",
    "http://mirror.arizona.edu/archlinux/$repo/os/$arch",
    "https://mirror.arizona.edu/archlinux/$repo/os/$arch",
    "http://arlm.tyzoid.com/$repo/os/$arch",
    "https://arlm.tyzoid.com/$repo/os/$arch",
    "http://ny.us.mirrors.bjg.at/arch/$repo/os/$arch",
    "https://ny.us.mirrors.bjg.at/arch/$repo/os/$arch",
    "http://mirrors.bloomu.edu/archlinux/$repo/os/$arch",
    "https://mirrors.bloomu.edu/archlinux/$repo/os/$arch",
    "https://arch-mirror.brightlight.today/$repo/os/$arch",
    "http://mirrors.cat.pdx.edu/archlinux/$repo/os/$arch",
    "http://us.mirrors.cicku.me/archlinux/$repo/os/$arch",
    "https://us.mirrors.cicku.me/archlinux/$repo/os/$arch",
    "http://mirror.clarkson.edu/archlinux/$repo/os/$arch",
    "https://mirror.clarkson.edu/archlinux/$repo/os/$arch",
    "http://mirror.colonelhosting.com/archlinux/$repo/os/$arch",
    "https://mirror.colonelhosting.com/archlinux/$repo/os/$arch",
    "http://arch.mirror.constant.com/$repo/os/$arch",
    "https://arch.mirror.constant.com/$repo/os/$arch",
    "http://mirror.cs.odu.edu/archlinux/$repo/os/$arch",
    "https://mirror.cs.odu.edu/archlinux/$repo/os/$arch",
    "http://mirror.cs.vt.edu/pub/ArchLinux/$repo/os/$arch",
    "http://repo.customcomputercare.com/archlinux/$repo/os/$arch",
    "https://repo.customcomputercare.com/archlinux/$repo/os/$arch",
    "http://distro.ibiblio.org/archlinux/$repo/os/$arch",
    "http://mirror.ette.biz/archlinux/$repo/os/$arch",
    "https://mirror.ette.biz/archlinux/$repo/os/$arch",
    "http://mirror.fcix.net/archlinux/$repo/os/$arch",
    "https://mirror.fcix.net/archlinux/$repo/os/$arch",
    "https://losangeles.mirror.pkgbuild.com/$repo/os/$arch",
    "http://mirrors.gigenet.com/archlinux/$repo/os/$arch",
    "https://mirror.givebytes.net/archlinux/$repo/os/$arch",
    "https://arch.goober.cloud/$repo/os/$arch",
    "http://mirror.hasphetica.win/archlinux/$repo/os/$arch",
    "https://mirror.hasphetica.win/archlinux/$repo/os/$arch",
    "http://arch.hu.fo/archlinux/$repo/os/$arch",
    "https://arch.hu.fo/archlinux/$repo/os/$arch",
    "http://arch.hugeblank.dev/$repo/os/$arch",
    "https://arch.hugeblank.dev/$repo/os/$arch",
    "http://repo.ialab.dsu.edu/archlinux/$repo/os/$arch",
    "https://repo.ialab.dsu.edu/archlinux/$repo/os/$arch",
    "https://mirrors.kernel.org/archlinux/$repo/os/$arch",
    "https://mirrors.lug.mtu.edu/archlinux/$repo/os/$arch",
    "https://ftp.osuosl.org/pub/archlinux/$repo/os/$arch",
    "https://mirror.pilotfiber.com/archlinux/$repo/os/$arch",
    "https://plug-mirror.rcac.purdue.edu/archlinux/$repo/os/$arch",
    "https://mirrors.rit.edu/archlinux/$repo/os/$arch",
    "https://mirrors.sonic.net/archlinux/$repo/os/$arch",
    "https://mirror.umd.edu/archlinux/$repo/os/$arch",
]
custom_servers = []
my_optional_repositories = [Repository.Multilib]
my_network_config_type = NicType.NM
my_bootloader = Bootloader.Systemd
my_uki = False
my_hostname = "yulia"
my_kernels = ["linux"]
my_ntp = False
my_packages = [
    "git",
    "rsync",
    "reflector",
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
my_parallel_downloads = 10
my_swap = True
my_timezone = "US/Eastern"
my_services = []
my_cc = []


# For Profiile Configuration
#
# profile_config = ProfileConfiguration(
#     profile=profile_handler.parse_profile_config(
#         {
#             "custom_settings": {
#                 "Niri": {
#                     "seat_access": "polkit",
#                 },
#             },
#             "details": ["Hyprland"],
#             "main": "Desktop",
#         }
#     ),
#     gfx_driver=GfxDriver.AmdOpenSource,
#     greeter=GreeterType.Ly,
# )
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

    with Installer(
        mountpoint,
        disk_config,
        base_packages=base_packages,
        kernels=config.kernels,
    ) as installation:
        # Mount all the drives to the desired mountpoint
        if disk_config.config_type != DiskLayoutType.Pre_mount:
            installation.mount_ordered_layout()

        installation.sanity_check()

        if disk_config.config_type != DiskLayoutType.Pre_mount:
            if (
                disk_config.disk_encryption
                and disk_config.disk_encryption.encryption_type
                != EncryptionType.NoEncryption
            ):
                # generate encryption key files for the mounted luks devices
                installation.generate_key_files()

        if mirror_config := config.mirror_config:
            installation.set_mirrors(mirror_config, on_target=False)

        installation.minimal_installation(
            optional_repositories=optional_repositories,
            mkinitcpio=run_mkinitcpio,
            hostname=arch_config_handler.config.hostname,
            locale_config=locale_config,
        )

        if mirror_config := config.mirror_config:
            installation.set_mirrors(mirror_config, on_target=True)

        if config.swap:
            installation.setup_swap("zram")

        if config.bootloader and config.bootloader != Bootloader.NO_BOOTLOADER:
            if config.bootloader == Bootloader.Grub and SysInfo.has_uefi():
                installation.add_additional_packages("grub")

            installation.add_bootloader(config.bootloader, config.uki)

        # If user selected to copy the current ISO network configuration
        # Perform a copy of the config
        network_config = config.network_config

        if network_config:
            network_config.install_network_config(
                installation,
                config.profile_config,
            )

        if config.auth_config:
            if config.auth_config.users:
                installation.create_users(config.auth_config.users)
                auth_handler.setup_auth(
                    installation, config.auth_config, config.hostname
                )

        if app_config := config.app_config:
            application_handler.install_applications(installation, app_config)

        if profile_config := config.profile_config:
            profile_handler.install_profile_config(installation, profile_config)

        if config.packages and config.packages[0] != "":
            installation.add_additional_packages(config.packages)

        if timezone := config.timezone:
            installation.set_timezone(timezone)

        if config.ntp:
            installation.activate_time_synchronization()

        if config.auth_config and config.auth_config.root_enc_password:
            root_user = User("root", config.auth_config.root_enc_password, False)
            installation.set_user_password(root_user)

        if (profile_config := config.profile_config) and profile_config.profile:
            profile_config.profile.post_install(installation)

        # If the user provided a list of services to be enabled, pass the list to the enable_service function.
        # Note that while it's called enable_service, it can actually take a list of services and iterate it.
        if servies := config.services:
            installation.enable_service(servies)

        if disk_config.has_default_btrfs_vols():
            btrfs_options = disk_config.btrfs_options
            snapshot_config = btrfs_options.snapshot_config if btrfs_options else None
            snapshot_type = snapshot_config.snapshot_type if snapshot_config else None
            if snapshot_type:
                installation.setup_btrfs_snapshot(snapshot_type, config.bootloader)

        # If the user provided custom commands to be run post-installation, execute them now.
        if cc := config.custom_commands:
            run_custom_user_commands(cc, installation)

        installation.genfstab()


def _minimal() -> None:
    # ------------- Assemble Config -----------------
    my_version = "archinstall"
    my_app_config = ApplicationConfiguration(
        bluetooth_config=BluetoothConfiguration(enabled=bluetooth_enable),
        audio_config=AudioConfiguration(audio=audio_config),
    )
    my_auth_config = AuthenticationConfiguration(
        root_enc_password=Password(plaintext="my_root_password"),
        users=[
            User(
                username=my_username,
                password=Password(plaintext="my_password"),
                sudo=my_sudo,
                groups=my_groups,
            ),
        ],
    )
    my_locale_config = LocaleConfiguration(
        kb_layout=my_kb_layout,
        sys_lang=my_sys_lang,
        sys_enc=my_sys_enc,
    )
    archinstall_language = translation_handler.get_language_by_abbr(arch_inst_lang)
    disk_config = DiskLayoutConfiguration(
        config_type=DiskLayoutType.Default,
        device_modifications=[],
        lvm_config=None,
        mountpoint=None,
    )
    my_profile_config = ProfileConfiguration(
        profile=my_profile,
        gfx_driver=my_gfx_driver,
        greeter=my_greeter,
    )
    my_mirror_config = MirrorConfiguration(
        mirror_regions=[
            MirrorRegion(
                name=my_country_name,
                urls=my_country_urls,
            ),
        ],
        custom_servers=[],
        optional_repositories=my_optional_repositories,
    )
    network_config = NetworkConfiguration(
        type=my_network_config_type,
    )
    bootloader = my_bootloader
    uki = my_uki
    hostname = my_hostname
    kernels = my_kernels
    ntp = my_ntp
    packages = my_packages
    parallel_downloads = my_parallel_downloads
    swap = my_swap
    timezone = my_timezone
    services = my_services
    custom_commands = my_cc

    # ------------- Write Config -----------------
    arch_config_handler.config.version = my_version
    arch_config_handler.config.locale_config = my_locale_config
    arch_config_handler.config.archinstall_language = archinstall_language
    arch_config_handler.config.profile_config = my_profile_config
    arch_config_handler.config.mirror_config = my_mirror_config
    arch_config_handler.config.network_config = network_config
    arch_config_handler.config.bootloader = bootloader
    arch_config_handler.config.uki = uki
    arch_config_handler.config.app_config = my_app_config
    arch_config_handler.config.auth_config = my_auth_config
    arch_config_handler.config.hostname = hostname
    arch_config_handler.config.kernels = kernels
    arch_config_handler.config.ntp = ntp
    arch_config_handler.config.packages = packages
    arch_config_handler.config.parallel_downloads = parallel_downloads
    arch_config_handler.config.swap = swap
    arch_config_handler.config.timezone = timezone
    arch_config_handler.config.services = services
    arch_config_handler.config.custom_commands = custom_commands

    with Tui():
        disk_config = DiskLayoutConfigurationMenu(disk_layout_config=None).run()
        arch_config_handler.config.disk_config = disk_config

    config = ConfigurationOutput(arch_config_handler.config)
    config.write_debug()
    config.save()

    if arch_config_handler.args.dry_run:
        exit(0)

    if not arch_config_handler.args.silent:
        aborted = False
        with Tui():
            if not config.confirm_config():
                debug("Installation aborted")
                aborted = True

        if aborted:
            return _minimal()

    if arch_config_handler.config.disk_config:
        fs_handler = FilesystemHandler(arch_config_handler.config.disk_config)
        fs_handler.perform_filesystem_operations()

    perform_installation(arch_config_handler.args.mountpoint)


_minimal()
