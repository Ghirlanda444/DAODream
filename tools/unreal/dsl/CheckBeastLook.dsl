(fn CheckBeastLook (Look)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid Look)
    (:then
      (Variabili|Predefinito|ImpostaBeastFoe (Matematica|Booleano|ORBoolean (Utilità|Stringa|Contains (Utilità|GetObjectName Look) "Mabari") (Utilità|Stringa|Contains (Utilità|GetObjectName Look) "GiantRat"))))))
