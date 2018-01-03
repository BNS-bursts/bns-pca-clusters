# Runtime Environment
Running the PCA codes requires:
1) swig-wrapped lal
2) sklearn
3) Assignment of environment variable BNSCLUSTERS_PREFIX which should point at
the top level of the repository and is used to find the waveform_data directory.
You can do this trivially inside the repo with: export BNSCLUSTERS_PREFIX=${PWD}

(1) and (2) should be handled easily via pip.  I (James) have a virtual
environment already set up for BNS work (pmr-dev) which satisfies these
requirements.   I can provide more details of that upon request.
