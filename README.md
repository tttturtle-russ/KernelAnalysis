# KernelAnalysis

1. Prerequisites(Tested On Ubuntu:24.04)
```
apt install fakeroot build-essential libncurses-dev xz-utils libssl-dev bc flex libelf-dev bison cmake gcc g++ zlib1g-dev libzstd-dev zip wget libncurses-dev python3
```

2. How to run
```
cd scripts
source setup.sh # build SVF and Linux Kernel
./analysis.sh # analysze bitcode
```

3. Techinique Details

- SVF: I modified the `MemSSA::dumpMSSA` function to make `wpa` output more suitable for our analysis.
```diff
diff --git a/svf/include/Graphs/ICFGNode.h b/svf/include/Graphs/ICFGNode.h
index 67fccfff..05b8ff92 100644
--- a/svf/include/Graphs/ICFGNode.h
+++ b/svf/include/Graphs/ICFGNode.h
@@ -587,7 +587,7 @@ public:
 
     const std::string getSourceLoc() const override
     {
-        return "CallICFGNode: " + ICFGNode::getSourceLoc();
+        return ICFGNode::getSourceLoc();
     }
 };
 
@@ -666,7 +666,7 @@ public:
 
     const std::string getSourceLoc() const override
     {
-        return "RetICFGNode: " + ICFGNode::getSourceLoc();
+        return ICFGNode::getSourceLoc();
     }
 };
 
diff --git a/svf/lib/MSSA/MemSSA.cpp b/svf/lib/MSSA/MemSSA.cpp
index d1347768..3f2581ae 100644
--- a/svf/lib/MSSA/MemSSA.cpp
+++ b/svf/lib/MSSA/MemSSA.cpp
@@ -584,25 +584,25 @@ void MemSSA::dumpMSSA(OutStream& Out)
 
         Out << "==========FUNCTION: " << fun->getName() << "==========\n";
         // dump function entry chi nodes
-        if (hasFuncEntryChi(fun))
-        {
-            CHISet & entry_chis = getFuncEntryChiSet(fun);
-            for (CHISet::iterator chi_it = entry_chis.begin(); chi_it != entry_chis.end(); chi_it++)
-            {
-                (*chi_it)->dump();
-            }
-        }
+        // if (hasFuncEntryChi(fun))
+        // {
+        //     CHISet & entry_chis = getFuncEntryChiSet(fun);
+        //     for (CHISet::iterator chi_it = entry_chis.begin(); chi_it != entry_chis.end(); chi_it++)
+        //     {
+        //         (*chi_it)->dump();
+        //     }
+        // }
 
         for (SVFFunction::const_iterator bit = fun->begin(), ebit = fun->end();
                 bit != ebit; ++bit)
         {
             const SVFBasicBlock* bb = *bit;
-            Out << bb->getName() << "\n";
-            PHISet& phiSet = getPHISet(bb);
-            for(PHISet::iterator pi = phiSet.begin(), epi = phiSet.end(); pi !=epi; ++pi)
-            {
-                (*pi)->dump();
-            }
+            // Out << bb->getName() << "\n";
+            // PHISet& phiSet = getPHISet(bb);
+            // for(PHISet::iterator pi = phiSet.begin(), epi = phiSet.end(); pi !=epi; ++pi)
+            // {
+            //     // (*pi)->dump();
+            // }
 
             bool last_is_chi = false;
             for (const auto& inst: bb->getICFGNodeList())
@@ -624,7 +624,7 @@ void MemSSA::dumpMSSA(OutStream& Out)
                         }
                     }
 
-                    Out << inst->toString() << "\n";
+                    // Out << inst->toString() << "\n";
 
                     if(hasCHI(cs))
                     {
@@ -642,9 +642,12 @@ void MemSSA::dumpMSSA(OutStream& Out)
                 else
                 {
                     bool dump_preamble = false;
+                    bool has_mu_or_chi = false;
+                    bool has_debug_info = !inst->getSourceLoc().empty();
+
                     SVFStmtList& pagEdgeList = mrGen->getPAGEdgesFromInst(inst);
                     for(SVFStmtList::const_iterator bit = pagEdgeList.begin(), ebit= pagEdgeList.end();
-                            bit!=ebit; ++bit)
+                            bit!=ebit && has_debug_info; ++bit)
                     {
                         const PAGEdge* edge = *bit;
                         if (const LoadStmt* load = SVFUtil::dyn_cast<LoadStmt>(edge))
@@ -657,16 +660,17 @@ void MemSSA::dumpMSSA(OutStream& Out)
                                     Out << "\n";
                                     dump_preamble = true;
                                 }
+                                has_mu_or_chi = true;
                                 (*it)->dump();
                             }
                         }
                     }
 
-                    Out << inst->toString() << "\n";
+                    // Out << inst->toString() << "\n";
 
                     bool has_chi = false;
                     for(SVFStmtList::const_iterator bit = pagEdgeList.begin(), ebit= pagEdgeList.end();
-                            bit!=ebit; ++bit)
+                            bit!=ebit && has_debug_info; ++bit)
                     {
                         const PAGEdge* edge = *bit;
                         if (const StoreStmt* store = SVFUtil::dyn_cast<StoreStmt>(edge))
@@ -675,10 +679,15 @@ void MemSSA::dumpMSSA(OutStream& Out)
                             for(CHISet::iterator it = chiSet.begin(), eit = chiSet.end(); it!=eit; ++it)
                             {
                                 has_chi = true;
+                                has_mu_or_chi = true;
                                 (*it)->dump();
                             }
                         }
                     }
+
+                    if (has_mu_or_chi && has_debug_info)
+                        Out << "SourceLoc->" << inst->getSourceLoc() << '\n';
+
                     if (has_chi)
                     {
                         Out << "\n";
@@ -691,13 +700,13 @@ void MemSSA::dumpMSSA(OutStream& Out)
         }
 
         // dump return mu nodes
-        if (hasReturnMu(fun))
-        {
-            MUSet & return_mus = getReturnMuSet(fun);
-            for (MUSet::iterator mu_it = return_mus.begin(); mu_it != return_mus.end(); mu_it++)
-            {
-                (*mu_it)->dump();
-            }
-        }
+        // if (hasReturnMu(fun))
+        // {
+        //     MUSet & return_mus = getReturnMuSet(fun);
+        //     for (MUSet::iterator mu_it = return_mus.begin(); mu_it != return_mus.end(); mu_it++)
+        //     {
+        //         (*mu_it)->dump();
+        //     }
+        // }
     }
 }

```
