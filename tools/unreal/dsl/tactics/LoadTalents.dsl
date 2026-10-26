(fn LoadTalents ()
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniTalIds))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniTalUse))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniTalNames))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniMemberIdx) 0)
    (:then
      (Funzionedichiamata|HeroTalents))
    (:else
      (Funzionedichiamata|NpcTalents))))
