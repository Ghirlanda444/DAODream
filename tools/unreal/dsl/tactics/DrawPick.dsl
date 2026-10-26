(fn DrawPick ()
  (Widget|SetText(Text) (Variabili|WBP_Tactics|OttieniPickTitle) (Utilità|Testo|ToText(String) (Utilità|Stringa|SelectString "Target" (Utilità|Stringa|SelectString "Condition" (Utilità|Stringa|SelectString "Action" "Click a field to change it" (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 4)) (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 2) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 3))) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 1))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 23
    (:LoopBody
      (Funzionedichiamata|DrawOpt :K _index))))
