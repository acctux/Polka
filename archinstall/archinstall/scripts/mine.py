from pathlib import Path
from importlib.metadata import version

from archinstall import SysInfo
from archinstall.lib.applications.application_handler import application_handler
from archinstall.lib.args import arch_config_handler
from archinstall.lib.authentication.authentication_handler import auth_handler
from archinstall.lib.configuration import ConfigurationOutput
from archinstall.lib.disk.disk_menu import DiskLayoutConfigurationMenu
from archinstall.lib.disk.filesystem import FilesystemHandler
from archinstall.lib.disk.utils import disk_layouts
from archinstall.lib.installer import (
    Installer,
    accessibility_tools_in_use,
    run_custom_user_commands,
)
from archinstall.lib.models import Bootloader
from archinstall.lib.models.device import (
    DiskLayoutType,
    EncryptionType,
)
from archinstall.lib.models.users import User
from archinstall.lib.output import debug, error, info
from archinstall.lib.profile.profiles_handler import profile_handler
from archinstall.tui import Tui
from archinstall.default_profiles.profile import GreeterType
from archinstall.lib.args import ArchConfig
from archinstall.lib.hardware import GfxDriver
from archinstall.lib.models.application import (
    ApplicationConfiguration,
    Audio,
    AudioConfiguration,
    BluetoothConfiguration,
)
from archinstall.lib.models.authentication import (
    AuthenticationConfiguration,
)
from archinstall.lib.models.locale import LocaleConfiguration
from archinstall.lib.models.mirrors import (
    MirrorConfiguration,
)
from archinstall.lib.models.network import NetworkConfiguration, NicType
from archinstall.lib.models.packages import Repository
from archinstall.lib.models.users import Password
from archinstall.lib.models.profile import ProfileConfiguration
from archinstall.lib.translationhandler import translation_handler

arch_config = ArchConfig(
    version=version("3.0.11"),
    script=None,
    app_config=ApplicationConfiguration(
        bluetooth_config=BluetoothConfiguration(enabled=True),
        audio_config=AudioConfiguration(audio=Audio.PIPEWIRE),
    ),
    auth_config=AuthenticationConfiguration(
        root_enc_password=None,
        users=[
            User(
                username="nick",
                password=Password(plaintext="test"),
                sudo=True,
                groups=["wheel"],
            ),
        ],
        u2f_config=None,
    ),
    locale_config=LocaleConfiguration(
        kb_layout="us",
        sys_lang="en_US.UTF-8",
        sys_enc="UTF-8",
    ),
    archinstall_language=translation_handler.get_language_by_abbr("en"),
    profile_config=ProfileConfiguration(
        profile=profile_handler.parse_profile_config(
            {
                "custom_settings": {
                    "Niri": {
                        "seat_access": "polkit",
                    },
                },
                "details": ["Niri"],
                "main": "Desktop",
            }
        ),
        gfx_driver=GfxDriver.AllOpenSource,
        greeter=GreeterType.Ly,
    ),
    mirror_config=MirrorConfiguration(
        mirror_regions=[],
        custom_servers=[],
        optional_repositories=[Repository.Multilib],
        custom_repositories=[],
    ),
    network_config=NetworkConfiguration(
        type=NicType.NM,
    ),
    bootloader=Bootloader.Systemd,
    uki=False,
    hostname="archlinux",
    kernels=["linux"],
    ntp=False,
    packages=["git", "rsync", "reflector"],
    parallel_downloads=0,
    swap=True,
    timezone="US/Eastern",
    services=[],
    custom_commands=[],
)
# arch_config = ArchConfig(
#     version=version("archinstall"),
#     script="test_script",
#     app_config=ApplicationConfiguration(
#         bluetooth_config=BluetoothConfiguration(enabled=True),
#         audio_config=AudioConfiguration(audio=Audio.PIPEWIRE),
#     ),
#     auth_config=AuthenticationConfiguration(
#         root_enc_password=Password(enc_password="password_hash"),
#         users=[
#             User(
#                 username="user_name",
#                 password=Password(enc_password="password_hash"),
#                 sudo=True,
#                 groups=["wheel"],
#             ),
#         ],
#         u2f_config=U2FLoginConfiguration(
#             u2f_login_method=U2FLoginMethod.Passwordless,
#             passwordless_sudo=True,
#         ),
#     ),
#     locale_config=LocaleConfiguration(
#         kb_layout="us",
#         sys_lang="en_US",
#         sys_enc="UTF-8",
#     ),
#     archinstall_language=translation_handler.get_language_by_abbr("en"),
#     disk_config=DiskLayoutConfiguration(
#         config_type=DiskLayoutType.Default,
#         device_modifications=[],
#         lvm_config=None,
#         mountpoint=None,
#     ),
#     profile_config=ProfileConfiguration(
#         profile=profile_handler.parse_profile_config(
#             {
#                 "custom_settings": {
#                     "Hyprland": {
#                         "seat_access": "polkit",
#                     },
#                     "Sway": {
#                         "seat_access": "seatd",
#                     },
#                 },
#                 "details": [
#                     "Sway",
#                     "Hyprland",
#                 ],
#                 "main": "Desktop",
#             }
#         ),
#         gfx_driver=GfxDriver.AllOpenSource,
#         greeter=GreeterType.Lightdm,
#     ),
#     mirror_config=MirrorConfiguration(
#         mirror_regions=[
#             MirrorRegion(
#                 name="Australia",
#                 urls=["http://archlinux.mirror.digitalpacific.com.au/$repo/os/$arch"],
#             ),
#         ],
#         custom_servers=[CustomServer("https://mymirror.com/$repo/os/$arch")],
#         optional_repositories=[Repository.Testing],
#         custom_repositories=[
#             CustomRepository(
#                 name="myrepo",
#                 url="https://myrepo.com/$repo/os/$arch",
#                 sign_check=SignCheck.Required,
#                 sign_option=SignOption.TrustAll,
#             ),
#         ],
#     ),
#     network_config=NetworkConfiguration(
#         type=NicType.MANUAL,
#         nics=[
#             Nic(
#                 iface="eno1",
#                 ip="192.168.1.15/24",
#                 dhcp=True,
#                 gateway="192.168.1.1",
#                 dns=[
#                     "192.168.1.1",
#                     "9.9.9.9",
#                 ],
#             ),
#         ],
#     ),
#     bootloader=Bootloader.Systemd,
#     uki=False,
#     hostname="archy",
#     kernels=["linux-zen"],
#     ntp=True,
#     packages=["firefox"],
#     parallel_downloads=66,
#     swap=False,
#     timezone="UTC",
#     services=["service_1", "service_2"],
#     custom_commands=["echo 'Hello, World!'"],
# )


def perform_installation(mountpoint: Path) -> None:
    """
    Perf orms the installation steps on a block device.
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

        if accessibility_tools_in_use():
            installation.enable_espeakup()

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

        debug(f"Disk states after installing:\n{disk_layouts()}")


def minimal() -> None:
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
            return minimal()

    if arch_config_handler.config.disk_config:
        fs_handler = FilesystemHandler(arch_config_handler.config.disk_config)
        fs_handler.perform_filesystem_operations()


minimal()
