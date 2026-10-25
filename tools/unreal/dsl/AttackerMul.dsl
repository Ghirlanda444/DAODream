(fn AttackerMul (Who)
  (Variabili|Predefinito|ImpostaTMul 1.0)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) Who (Gioco|GetPlayerPawn 0))
    (:then
      (Variabili|Predefinito|ImpostaTMul (Utility|Operatori|Moltiplica (Matematica|Float|SelectFloat 0.8 1.0 (Classe|BPPlotManager|OttieniRogue (Variabili|Predefinito|OttieniMgr))) (Matematica|Float|SelectFloat 2.0 1.0 (Classe|BPPlotManager|OttieniThreatenOn (Variabili|Predefinito|OttieniMgr))))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid Who)
        (:then
          (Funzionedichiamata|NpcMul :Who Who))))))
