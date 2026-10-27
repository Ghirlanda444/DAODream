(fn DrawIt (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Classe|BPContainer|OttieniLItems (Variabili|Predefinito|OttieniBox))))
    (:then
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItBs) K) "Visible")
      (Widget|SetText(Text) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItTs) K) (Utilità|Testo|ToText(String) (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniItemNames (Variabili|Predefinito|OttieniMgr)) (Utilità|Array|Ottieni(unacopia) (Classe|BPContainer|OttieniLItems (Variabili|Predefinito|OttieniBox)) K)) " x") (Utilità|Stringa|ToString(Integer) (Utilità|Array|Ottieni(unacopia) (Classe|BPContainer|OttieniLCounts (Variabili|Predefinito|OttieniBox)) K))))))
    (:else
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItBs) K) "Collapsed"))))
