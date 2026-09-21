{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    gnumake
  ];

  # PYTHONPATH: replaces whatever the calling shell had (a stale entry there
  # shadows the venv) and puts the repo root on the path so `import radar` works.
  # LD_LIBRARY_PATH: pip wheels expect libstdc++.so.6 where NixOS doesn't keep it.
  shellHook = ''
    export PYTHONPATH=$PWD
    export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.zlib ]}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
    make setup
    if [[ -d venv ]]; then
      source venv/bin/activate
    fi
  '';
}
