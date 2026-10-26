(fn GiveNpcImmortal (Npc K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniNpcImmortal)))
    (:then
      (Classe|BPDlgNPC|SetImmortal Npc (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcImmortal) K) 1)))))
