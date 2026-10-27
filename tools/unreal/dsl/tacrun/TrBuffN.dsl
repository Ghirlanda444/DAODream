(fn TrBuffN (N K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Classe|BPDlgNPC|OttieniNOn N))) (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica K 18) (Utilità|Array|Length (Classe|BPDlgNPC|OttieniNTalents N))))
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Classe|BPDlgNPC|OttieniNOn N) K) 0.0) (Utilità|Array|ContainsItem (Variabili|Predefinito|OttieniTBuffs) (Utilità|Array|Ottieni(unacopia) (Classe|BPDlgNPC|OttieniNTalents N) (Utility|Operatori|Moltiplica K 18))))
    (:then
      (Variabili|Predefinito|ImpostaPkBuff "true"))))))
