{ pkgs ? import
    (fetchTarball {
      name = "jpetrucciani-2025-05-16";
      url = "https://github.com/jpetrucciani/nix/archive/2e6d24744e04b13cba328c071a1f5482bcf4c6d6.tar.gz";
      sha256 = "1iy5w26x5k317k324f0dg0fx72dq96yrqpfkv7zcjccg1n2cp58w";
    })
    { }
}:
let
  name = "coffee_order";

  uvEnv = pkgs.uv-nix.mkEnv {
    inherit name; python = pkgs.python313;
    workspaceRoot = ./.;
    pyprojectOverrides = final: prev: { };
  };

  tools = with pkgs; {
    cli = [
      jfmt
      nixup
    ];
    uv = [ uv uvEnv ];
    scripts = pkgs.lib.attrsets.attrValues scripts;
  };

  scripts = with pkgs; { };
  paths = pkgs.lib.flatten [ (builtins.attrValues tools) ];
  env = pkgs.buildEnv {
    inherit name paths; buildInputs = paths;
  };
in
(env.overrideAttrs (_: {
  inherit name;
  NIXUP = "0.0.9";
} // uvEnv.uvEnvVars)) // { inherit scripts; }
