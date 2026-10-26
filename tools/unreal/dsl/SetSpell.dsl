(fn SetSpell (InSpell K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length InSpell) (Utility|Operatori|Aggiungi K 1))
    (:then
      (Variabili|Predefinito|ImpostaSpellPower (Utilità|Array|Ottieni(unacopia) InSpell K))
      (Variabili|Predefinito|ImpostaStaff (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) InSpell (Utility|Operatori|Aggiungi K 1)) 0.5)))))
