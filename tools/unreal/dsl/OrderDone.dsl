(fn OrderDone (Follower)
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniControlled Follower)
    (:then
      (Classe|BPDlgNPC|DropTarget Follower))
    (:else
      (Funzionedichiamata|AssignByBid :Follower Follower))))
