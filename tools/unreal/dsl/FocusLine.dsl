(fn FocusLine (Idx)
  (bind _raw (Funzionedichiamata|LineStr :Idx Idx :Field "Speaker"))
  (bind _found (Attore|GetAllActorsOfClasswithTag :ActorClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C" :Tag (Utilità|Stringa|StringToName _raw)))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|Stringa|EqualExactly(String) _raw "OWNER")
    (:then
      (Classe|BPPlotManager|FocusSpeaker (Variabili|Predefinito|OttieniMgr) :Speaker (Componenti|GetOwner (Variabili|Ottieniunriferimentoasestesso))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length _found) 0)
        (:then
          (Classe|BPPlotManager|FocusSpeaker (Variabili|Predefinito|OttieniMgr) :Speaker (Utilità|Array|Ottieni(unacopia) _found 0)))))))
