(fn SupportAct ()
  (Funzionedichiamata|MayFight)
  (Classe|BPPlotManager|TrFoeTest (Variabili|Predefinito|OttieniMgr) :A (Variabili|Predefinito|OttieniTacWho))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTacSlot) 0)
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPPlotManager|OttieniBFoe (Variabili|Predefinito|OttieniMgr))
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniBMay)
    (:then
      (Funzionedichiamata|TacSetTarget)
      (Variabili|Predefinito|ImpostaPendingSlot (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniTacSlot) 1)))))
    (:else
      (Funzionedichiamata|DoTalent))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniTacDone) (Classe|BPPlotManager|OttieniBFoe (Variabili|Predefinito|OttieniMgr))) (Variabili|Predefinito|OttieniBMay))
    (:then
      (Funzionedichiamata|TacSetTarget))
    (:else
      (Funzionedichiamata|AttackBackCheck))))))
