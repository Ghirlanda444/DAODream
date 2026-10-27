(fn BidChoose (Follower)
  (Classe|BPDlgNPC|MayFight Follower)
  (Funzionedichiamata|TrCtrl)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Classe|BPDlgNPC|OttieniBMay Follower) (Utilità|IsValid (Variabili|Predefinito|OttieniBestTarget)))
    (:then
      (Funzionedichiamata|BidAttack :Follower Follower))
    (:else
      (Classe|BPDlgNPC|SetTarget Follower))))
