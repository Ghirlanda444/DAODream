(fn DrawOpt (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptNames)))
    (:then
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptBs) K) "Visible")
      (Widget|SetText(Text) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptTs) K) (Utilità|Testo|ToText(String) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptNames) K))))
    (:else
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptBs) K) "Collapsed"))))
