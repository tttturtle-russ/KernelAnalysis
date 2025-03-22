# KernelAnalysis

1. Prerequisites(Tested On Ubuntu:24.04)

```
apt install fakeroot build-essential libncurses-dev xz-utils libssl-dev bc flex libelf-dev bison cmake gcc g++ zlib1g-dev libzstd-dev zip wget libncurses-dev python3 python3-venv python3-pip file
```

2. How to run

```
cd scripts
source setup.sh # build SVF and Linux Kernel
./analysis.sh # analysze bitcode
```

3. Techinique Details

- Syzkaller: We use the modified syzkaller from [HBFourier](https://figshare.com/articles/code/HBFourier_Artifact/25365340?file=44924227), also we add some functions to make it more functional. See this [directory](./patches/syzkaller/).

- SVF: We modified the `MemSSA::dumpMSSA` function and `ICFGCallNode::getSourceLoc` to make `wpa` output more suitable for our analysis. See this [directory](./patches/svf/)

**Note that these patches may contain commit changes from upstream, in case you want to take a look at our modification, focus on the following files:**
- [MemSSA.cpp](./SVF/svf/lib/MSSA/MemSSA.cpp)
- [MSSAMuChi.h](./SVF/svf/include/MSSA/MSSAMuChi.h)
- [ICFGNode.h::getSourceLoc](./SVF/svf/include/Graphs/ICFGNode.h)
