(fn DrawPick ()
  (Widget|SetText(Text) (Variabili|WBP_Tactics|OttieniPickTitle) (Utilità|Testo|ToText(String) (Utilità|Stringa|SelectString "Behaviour" (Utilità|Stringa|SelectString "Preset (fills the slots)" (Utilità|Stringa|SelectString "Target" (Utilità|Stringa|SelectString "Condition" (Utilità|Stringa|SelectString "Action" "Click a field to change it" (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 4)) (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 2) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 3))) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 1)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 5)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 6))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 31
    (:LoopBody
      (Funzionedichiamata|DrawOpt :K _index))))
