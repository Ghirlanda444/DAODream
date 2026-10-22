(fn EnsureDlgCam ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniDlgCam))
    (:else
      (Variabili|Predefinito|ImpostaDlgCam (Gioco|Generaattoredallaclasse :Class "/Game/Cousland/Dialogue/BP_DlgCam.BP_DlgCam_C" :SpawnTransform (Matematica|Trasforma|MakeTransform (Matematica|Vettore|MakeVector 0.0 0.0 0.0)))))))
