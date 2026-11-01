object NEnsembleActivityFrame: TNEnsembleActivityFrame
  Left = 0
  Top = 0
  Width = 508
  Height = 367
  TabOrder = 0
  object Panel1: TPanel
    Left = 0
    Top = 0
    Width = 508
    Height = 367
    Align = alClient
    TabOrder = 0
    inline WatchFrame: TWatchFrame
      Left = 1
      Top = 1
      Width = 506
      Height = 365
      Align = alClient
      TabOrder = 0
      TabStop = True
      ExplicitLeft = 1
      ExplicitTop = 1
      ExplicitWidth = 506
      ExplicitHeight = 365
      inherited Chart1: TChart
        Width = 506
        Height = 365
        ExplicitWidth = 506
        ExplicitHeight = 365
      end
    end
  end
end
