object SourcesControlForm: TSourcesControlForm
  Left = 0
  Top = 0
  Caption = 'SourcesControlForm'
  ClientHeight = 408
  ClientWidth = 577
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  inline NSourceControlFrame: TNSourceControlFrame
    Left = 0
    Top = 0
    Width = 577
    Height = 408
    Align = alClient
    TabOrder = 0
    ExplicitLeft = -164
    ExplicitTop = -169
    inherited Splitter1: TSplitter
      Width = 577
    end
    inherited Panel1: TPanel
      Width = 577
      inherited SourceWatchFrame: TWatchFrame
        Width = 575
        ExplicitLeft = 1
        ExplicitTop = 1
        ExplicitWidth = 588
        ExplicitHeight = 175
        inherited Chart1: TChart
          Width = 575
          ExplicitWidth = 588
          ExplicitHeight = 175
        end
      end
    end
    inherited Panel2: TPanel
      Width = 577
      Height = 228
      ExplicitLeft = 0
      ExplicitTop = 180
      ExplicitWidth = 590
      ExplicitHeight = 212
      inherited GroupBox1: TGroupBox
        Width = 378
        Height = 226
        ExplicitLeft = 1
        ExplicitTop = 1
        ExplicitWidth = 391
        ExplicitHeight = 210
        inherited SourcesStringGrid: TStringGrid
          Width = 374
          Height = 209
          ExplicitLeft = 2
          ExplicitTop = 15
          ExplicitWidth = 387
          ExplicitHeight = 193
        end
      end
      inherited Panel3: TPanel
        Left = 379
        Height = 226
        inherited FrequencyGroupBox: TGroupBox
          ExplicitLeft = 1
          ExplicitTop = 49
        end
      end
    end
  end
end
