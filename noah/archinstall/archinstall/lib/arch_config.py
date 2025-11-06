from importlib.metadata import version

from archinstall.default_profiles.profile import GreeterType
from archinstall.lib.args import ArchConfig
from archinstall.lib.hardware import GfxDriver
from archinstall.lib.models.application import (
    ApplicationConfiguration,
    Audio,
    AudioConfiguration,
    BluetoothConfiguration,
)
from archinstall.lib.models.authentication import AuthenticationConfiguration
from archinstall.lib.models.bootloader import Bootloader
from archinstall.lib.models.locale import LocaleConfiguration
from archinstall.lib.models.mirrors import MirrorConfiguration
from archinstall.lib.models.network import NetworkConfiguration, NicType
from archinstall.lib.models.profile import ProfileConfiguration
from archinstall.lib.models.users import Password, User
from archinstall.lib.profile.profiles_handler import profile_handler
from archinstall.lib.translationhandler import translation_handler

ARCH_CONFIG = ArchConfig(
    version=version("archinstall"),
    script=None,
    locale_config=LocaleConfiguration(
        kb_layout="us",
        sys_lang="en_US.UTF-8",
        sys_enc="UTF-8",
    ),
    archinstall_language=translation_handler.get_language_by_abbr("en"),
    disk_config=None,
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
        optional_repositories=[],
        custom_repositories=[],
    ),
    network_config=NetworkConfiguration(
        type=NicType.NM,
    ),
    bootloader=Bootloader.Systemd,
    uki=False,
    app_config=ApplicationConfiguration(
        bluetooth_config=BluetoothConfiguration(enabled=True),
        audio_config=AudioConfiguration(audio=Audio.PIPEWIRE),
    ),
    auth_config=AuthenticationConfiguration(
        root_enc_password=Password(plaintext="test"),
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
