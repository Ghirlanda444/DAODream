(fn DrawTab (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minoreuguale(<=) K (Utilità|Array|Length (Variabili|Predefinito|OttieniMembers)))
    (:then
      (Funzionedichiamata|TabName :K K)
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMemBs) K) "Visible")
      (Widget|SetText(Text) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMemTs) K) (Utilità|Testo|ToText(String) (Variabili|Predefinito|OttieniMName))))
    (:else
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMemBs) K) "Collapsed"))))
