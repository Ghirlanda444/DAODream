(fn ShowTalents ()
  (Variabili|Predefinito|ImpostaTalentText "")
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalentNames)) 1)
    (:LoopBody
      (Funzionedichiamata|AddTalentLine :Slot _index))
    (:Completed
      (Classe|WBPCombatHUD|SetTalents (Variabili|Predefinito|OttieniHud) :Txt (Variabili|Predefinito|OttieniTalentText)))))
