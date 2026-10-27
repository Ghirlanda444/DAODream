(fn SetupHero ()
  (Variabili|Predefinito|ImpostaMBeh (Classe|BPPlotManager|OttieniPBehavior (Variabili|Predefinito|OttieniMgr)))
  (Funzionedichiamata|DrawSetup)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Classe|BPPlotManager|OttieniPTraits (Variabili|Predefinito|OttieniMgr))) 0)
    (:then
      (Variabili|Predefinito|ImpostaMClass (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniPTraits (Variabili|Predefinito|OttieniMgr)) 0))))))
