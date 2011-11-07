object MuscleTestForm: TMuscleTestForm
  Left = 0
  Top = 350
  Caption = #1056#1077#1072#1082#1094#1080#1080' '#1085#1077#1081#1088#1086#1085#1086#1074
  ClientHeight = 238
  ClientWidth = 1008
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poDesigned
  PixelsPerInch = 96
  TextHeight = 13
  object PageControl1: TPageControl
    Left = 0
    Top = 0
    Width = 1008
    Height = 238
    ActivePage = TabSheet1
    Align = alClient
    TabOrder = 0
    object TabSheet1: TTabSheet
      Caption = #1056#1077#1072#1082#1094#1080#1103' '#1076#1074#1080#1075#1072#1090#1077#1083#1103
      inline SingleMuscleWatchFrame: TWatchFrame
        Left = 0
        Top = 0
        Width = 1000
        Height = 210
        Align = alClient
        TabOrder = 0
        TabStop = True
        ExplicitWidth = 1000
        ExplicitHeight = 210
        inherited Chart1: TChart
          Width = 1000
          Height = 210
          ExplicitWidth = 1000
          ExplicitHeight = 210
        end
      end
    end
    object TabSheet2: TTabSheet
      Caption = #1055#1072#1088#1072' '#1084#1099#1096#1094
      ImageIndex = 1
      TabVisible = False
      inline DoubleMuscleWatchFrame: TWatchFrame
        Left = 0
        Top = 0
        Width = 1000
        Height = 210
        Align = alClient
        TabOrder = 0
        TabStop = True
        ExplicitWidth = 1000
        ExplicitHeight = 210
        inherited Chart1: TChart
          Width = 1000
          Height = 210
          ExplicitWidth = 1000
          ExplicitHeight = 210
        end
      end
    end
    object TabSheet3: TTabSheet
      Caption = #1040#1092#1092#1077#1088#1077#1090#1085#1099#1077' '#1087#1086#1090#1086#1082#1080
      ImageIndex = 2
      inline AfferentWatchFrame: TWatchFrame
        Left = 0
        Top = 0
        Width = 1000
        Height = 210
        Align = alClient
        TabOrder = 0
        TabStop = True
        ExplicitWidth = 1000
        ExplicitHeight = 210
        inherited Chart1: TChart
          Width = 1000
          Height = 210
          ExplicitWidth = 1000
          ExplicitHeight = 210
        end
      end
    end
    object TabSheet4: TTabSheet
      Caption = #1054#1057' '#1052#1086#1090#1086#1085#1077#1081#1088#1086#1085'-'#1050#1083'. '#1056#1077#1085#1096#1086#1091
      ImageIndex = 3
      inline FBMotoneuronWatchFrame: TWatchFrame
        Left = 0
        Top = 0
        Width = 1000
        Height = 210
        Align = alClient
        TabOrder = 0
        TabStop = True
        ExplicitWidth = 1000
        ExplicitHeight = 210
        inherited Chart1: TChart
          Width = 1000
          Height = 210
          ExplicitWidth = 1000
          ExplicitHeight = 210
        end
      end
    end
    object TabSheet5: TTabSheet
      Caption = #1063#1072#1089#1090#1086#1090#1099' '#1052#1053'-'#1056#1077#1085#1096#1086#1091
      ImageIndex = 4
      TabVisible = False
      inline MotoneuronFrequencyWatchFrame: TWatchFrame
        Left = 0
        Top = 0
        Width = 1000
        Height = 210
        Align = alClient
        TabOrder = 0
        TabStop = True
        ExplicitWidth = 1000
        ExplicitHeight = 210
        inherited Chart1: TChart
          Width = 1000
          Height = 210
          ExplicitWidth = 1000
          ExplicitHeight = 210
        end
      end
    end
    object TabSheet6: TTabSheet
      Caption = #1042#1089#1103' '#1089#1077#1090#1100
      ImageIndex = 5
      inline NetworkWatchFrame: TWatchFrame
        Left = 0
        Top = 0
        Width = 1000
        Height = 210
        Align = alClient
        TabOrder = 0
        TabStop = True
        ExplicitWidth = 1000
        ExplicitHeight = 210
        inherited Chart1: TChart
          Width = 1000
          Height = 210
          ExplicitWidth = 1000
          ExplicitHeight = 210
        end
      end
    end
    object TabSheet7: TTabSheet
      Caption = #1042#1089#1103' '#1089#1077#1090#1100' ('#1095#1072#1089#1090#1086#1090#1099')'
      ImageIndex = 6
      TabVisible = False
      inline FNetworkWatchFrame: TWatchFrame
        Left = 0
        Top = 0
        Width = 1000
        Height = 210
        Align = alClient
        TabOrder = 0
        TabStop = True
        ExplicitWidth = 1000
        ExplicitHeight = 210
        inherited Chart1: TChart
          Width = 1000
          Height = 210
          ExplicitWidth = 1000
          ExplicitHeight = 210
        end
      end
    end
  end
end
