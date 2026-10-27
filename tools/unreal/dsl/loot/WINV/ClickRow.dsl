(fn ClickRow (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Classe|BPPlotManager|OttieniInv (Variabili|Predefinito|OttieniMgr))))
    (:then
      (Widget|SetText(Text) (Variabili|WBP_Inventory|OttieniDesc) (Utilità|Testo|ToText(String) (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniItemDescs (Variabili|Predefinito|OttieniMgr)) (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniInv (Variabili|Predefinito|OttieniMgr)) K))))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniItemStats (Variabili|Predefinito|OttieniMgr)) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniInv (Variabili|Predefinito|OttieniMgr)) K) 6) 0)) 1.0) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniItemStats (Variabili|Predefinito|OttieniMgr)) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniInv (Variabili|Predefinito|OttieniMgr)) K) 6) 0)) 2.0))
    (:then
      (Classe|BPPlotManager|UseFromInv (Variabili|Predefinito|OttieniMgr) :Slot K)
      (Funzionedichiamata|Redraw))))))
