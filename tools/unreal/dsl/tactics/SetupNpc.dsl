(fn SetupNpc ()
  (Variabili|Predefinito|ImpostaMBeh (Classe|BPDlgNPC|OttieniBehavior (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1))))
  (Funzionedichiamata|DrawSetup)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Classe|BPDlgNPC|OttieniNTraits (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1)))) 0)
    (:then
      (Variabili|Predefinito|ImpostaMClass (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) (Classe|BPDlgNPC|OttieniNTraits (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1))) 0))))))
