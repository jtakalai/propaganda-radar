{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    sqlite
    python3
    python3Packages.pip
    python3Packages.matplotlib
    python3Packages.numpy
    python3Packages.pandas
    python3Packages.networkx
    python3Packages.seaborn
    python3Packages.scipy
    python3Packages.scikit-learn
    python3Packages.nltk
    python3Packages.feedparser
    python3Packages.deep-translator
  ];
}
