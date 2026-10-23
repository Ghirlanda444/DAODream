(fn CreateKitISMs ()
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniKitISMs))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniKitMeshes)) 1)
    (:LoopBody
      (bind _c (Aggiungicomponente|Rendering|AggiungiInstancedStaticMeshComponent :bManualAttachment "false" :RelativeTransform (Matematica|Trasforma|MakeTransform (Matematica|Vettore|MakeVector 0.0 0.0 0.0))))
      (Componenti|StaticMesh|SetStaticMesh _c (Utilità|Casting|CastToStaticMesh (Utilità|LoadAssetBlocking (Utilità|ToSoftObjectReference (Utilità|MakeSoftObjectPath (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniKitMeshes) _index))))))
      (Utilità|Array|Add (Variabili|Predefinito|OttieniKitISMs) _c))))
