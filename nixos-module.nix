{ pkgs, lib, config, ... }:
let
  cfg = config.services.blurred-horse-bot;
  defaultUser = "blurred-horse-bot";
in with lib; {
  options.services.blurred-horse-bot = {
    enable = mkEnableOption "blurred-horse-bot";
    user = mkOption {
      type = types.str;
      description = "User to run under";
      default = defaultUser;
    };
    group = mkOption {
      type = types.str;
      description = "Group to run under";
      default = defaultUser;
    };
    postOnCalendar = mkOption {
      type = types.str;
      description = "systemd OnCalendar specification";
      default = "*-*-* *:00:00";
    };

    appSecret = mkOption {
      type = types.path;
      description = ''
        Path to file containing the server and a bunch of secret crap.
        This file is generated from create_app() in mastodon.py. See the
        mastodon.py repo for more info:

        https://github.com/halcy/Mastodon.py
      '';
      default = "/var/lib/secrets/blurred-horse-bot/app.secret";
    };

    environmentFile = mkOption {
      type = types.path;
      description = ''
        Path to file containing environment variables in standard environment
        file format. This file must contain definitions for the following variables:
        FLICKR_API, FLICKR_SECRET, MASTODON_EMAIL, and MASTODON_PASSWORD.
      '';
      default = "/var/lib/secrets/blurred-horse-bot/secrets.env";
    };
  };

  config = mkIf cfg.enable {
    systemd.services.blurred-horse-bot-config = {
      description = "Set up blurred-horse-bot required directories";
      environment = { inherit (cfg) user group appSecret; };

      script = ''
        mkdir -p "$(dirname "$appSecret")" "$(dirname "$environmentFile")"
        touch "$appSecret" "$environmentFile"

        chown -R "$user:$group" "$(dirname "$appSecret")" "$(dirname "$environmentFile")"
      '';
    };

    systemd.services.blurred-horse-bot = {
      description = "Blurred Horse Bot";
      wants = [ "blurred-horse-bot-config.service" ];

      environment.MASTODON_APPDATA = cfg.appSecret;

      unitConfig = {
        ConditionPathExists = [ cfg.appSecret ];
      };

      serviceConfig = {
        ExecStart = "${pkgs.blurred-horse-bot}/bin/blurred-horse-bot";
        User = cfg.user;
        Group = cfg.group;
        EnvironmentFile = cfg.environmentFile;
      };
    };

    systemd.timers.blurred-horse-bot = {
      wantedBy = [ "network-online.target" ];
      timerConfig.OnCalendar = cfg.postOnCalendar;
    };

    users.users = optionalAttrs (cfg.user == defaultUser) {
      ${defaultUser} = {
        group = cfg.group;
        isSystemUser = true;
      };
    };

    users.groups =
      optionalAttrs (cfg.group == defaultUser) { ${defaultUser} = { }; };
  };
}
