(fn GainHealth (Amount)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniDead)
    (:else
      (Variabili|Predefinito|ImpostaHealth (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniHealth) Amount) (Variabili|Predefinito|OttieniMaxHealth)))
      (Funzionedichiamata|ShowHealthText)
      (Funzionedichiamata|SayText :Txt (Utilità|Stringa|Append "+" (Utilità|Stringa|ToString(Integer) (Matematica|Float|Truncate Amount)))))))
