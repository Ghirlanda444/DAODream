(fn BidAttack (Follower)
  (Classe|BPDlgNPC|NFlag Follower :Fl 7)
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniBFlag Follower)
    (:then
      (Funzionedichiamata|BidReach :Follower Follower))
    (:else
      (Funzionedichiamata|BidKeep :Follower Follower))))
