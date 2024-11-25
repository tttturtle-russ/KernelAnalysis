- [x] 1. Cmake version need to be no lower than 3.23.0
- [x] 2. CONFIG_DIR lacks the linux version, now just added manually
- [x] 3. No clang version check?
- [ ] 4. If error, echo error info on the terminal but not only in the log.
- [ ] 5. After installing llvm, clang, z3, etc. as a user, /bin/* is not ln to /usr/local/bin
- [ ] 6. Too many symbol multiply defined while linking
- [ ] 7. Assertion failed during wpa, smiliar to the 6 point.
    ```bash
    wpa: /home/kddrca/KernelAnalysis/SVF/svf/include/Graphs/VFG.h:417: void SVF::VFG::setDef(const SVF::PAGNode*, const SVF::VFGNode*): Assertion (it->second == node->getId()) && "a SVFVar can only have unique definition "' failed.
    ./analysis.sh: line 35: 216980 Aborted                 (core dumped) wpa -ander -cxt -opt-svfg -race -stat=false -dump-mssa -ind-call-limit=100000 -svfg "$bcfile" > "$dir/mssa.$name"
    ```
- [ ] 8. genmempair.py, whatif the write_set or the read_set is empty, no result
- [ ] 9. vcall gep idx not constantint, also the wpa error
- [ ] 10. other wpa errors, have not check carefully
- [ ] 11. Warnings should not display while compiling
- [ ] 12. Uniq mempairs by different ways are different