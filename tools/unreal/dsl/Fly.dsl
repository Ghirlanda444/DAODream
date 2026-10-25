(fn Fly ()
  (Variabili|Predefinito|ImpostaAT (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniAT) 0.0667) 1.0))
  (Trasformazione|SetActorLocation (Variabili|Ottieniunriferimentoasestesso) (Matematica|Vettore|Lerp(Vector) (Variabili|Predefinito|OttieniAFrom) (Variabili|Predefinito|OttieniATo) (Variabili|Predefinito|OttieniAT)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniAT) 1.0)
    (:then
      (Attore|DestroyActor (Variabili|Ottieniunriferimentoasestesso)))))
