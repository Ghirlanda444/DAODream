(fn StageAll ()
  (bind _i (Matematica|Intero|Min(Integer) (Matematica|Float|Truncate (Utility|Operatori|Moltiplica (Utility|Operatori|Sottrai (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniStageStart)) (Variabili|Predefinito|OttieniStageRate))) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniStageN) 1)))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniStageTags)) 1)
    (:LoopBody (Funzionedichiamata|StagePlace :K _index :I _i))))
