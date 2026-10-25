(fn SetPlayerSeen (InStats)
  (Variabili|Predefinito|ImpostaPSeen 20.0)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length InStats) 19)
    (:then
      (Variabili|Predefinito|ImpostaPSeen (Utilità|Array|Ottieni(unacopia) InStats 19)))))
