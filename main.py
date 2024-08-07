import os
import json

path_env_var = os.getenv('PATH')
paths = path_env_var.split(os.pathsep)

config = json.load(open("config.json"))


def check_in_path(__cmd):
    in_path = False
    for path in paths:
        try:
            if __cmd in os.listdir(path):
                in_path = True
                break
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            continue

    print(f"'{__cmd}' is in PATH:", in_path)
    return in_path


def gen_cmd():
    __cmds = []
    extra_cmd = ""
    bin_path = config["bin_path"]
    n_m3u8dl_bin = bin_path.get("N_m3u8DL-RE", "")
    if not n_m3u8dl_bin and not check_in_path("N_m3u8DL-CLI"):
        print("N_m3u8DL-CLI not found in PATH")
        exit(1)

    dl_url = config.get("m3u8_url")

    dl_settings = config["N_m3u8DL_setting"]
    if save_dir := dl_settings.get("save_dir"):
        extra_cmd += f' --save-dir "{save_dir}"'
    if save_name := dl_settings.get("save_name"):
        extra_cmd += f' --save-name "{save_name}"'
    if headers := dl_settings.get("headers"):
        for header in headers:
            extra_cmd += f' -H "{header}"'
    if extra_args := dl_settings.get("extra_args"):
        for extra_arg in extra_args:
            extra_cmd += f' {extra_arg}'
    if key_text_file := dl_settings.get("key_text_file"):
        extra_cmd += f' --key-text-file "{key_text_file}"'

    df_aud_lang = dl_settings.get("default_audio_language", "en")
    de_aud_id = dl_settings.get("default_audio_id", "")
    df_ss = dl_settings.get("default_subtitle_language", "all")
    df_ss_id = dl_settings.get("default_subtitle_id", "")
    if df_ss == "all" or df_ss == "":
        ss_lang_cmd = ""
    else:
        ss_lang_cmd = f'lang={df_ss}:'

    download_definition = config.get("download_definition", ["1080p"])
    for definition in download_definition:
        # add video, audio, subtitle, etc. settings
        __extra_cmd = extra_cmd
        if definition == "1080p":
            __extra_cmd += ' -sv res="19*":codecs="avc1*":range=SDR:for=best'
        elif definition == "4k":
            __extra_cmd += f' -sv codecs="hvc1*":range=SDR:for=best'
        elif definition == "4k_hdr":
            __extra_cmd += f' -sv codecs="hvc1*":range=PQ:for=best'
        elif definition == "4k_dv":
            __extra_cmd += f' -sv codecs="dvh1*":range=PQ:for=best'

        __extra_cmd += f' -sa id={de_aud_id}:lang={df_aud_lang}:for=best'
        __extra_cmd += f' -ss id={df_ss_id}:{ss_lang_cmd}for=all'

        __cmd = f'{n_m3u8dl_bin} {__extra_cmd} "{dl_url}"'
        __cmds.append(__cmd)
    return __cmds


if __name__ == "__main__":
    cmds = gen_cmd()
    for cmd in cmds:
        print(cmd)
