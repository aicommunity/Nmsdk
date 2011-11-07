object LinksForm: TLinksForm
  Left = 0
  Top = 0
  Caption = 'LinksForm'
  ClientHeight = 450
  ClientWidth = 635
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  inline NLinksFrame: TNLinksFrame
    Left = 0
    Top = 0
    Width = 635
    Height = 450
    Align = alClient
    TabOrder = 0
    ExplicitLeft = 15
    ExplicitTop = 22
    inherited Splitter1: TSplitter
      Top = 240
      Width = 635
    end
    inherited GroupBox1: TGroupBox
      Left = 330
      Height = 240
      inherited NANetFrameInputs: TNANetFrame
        Height = 223
        inherited StringGrid: TStringGrid
          Height = 223
        end
      end
    end
    inherited GroupBox2: TGroupBox
      Width = 330
      Height = 240
      inherited NANetFrameOutputs: TNANetFrame
        Width = 326
        Height = 223
        inherited StringGrid: TStringGrid
          Width = 326
          Height = 223
        end
      end
    end
    inherited GroupBox3: TGroupBox
      Top = 247
      Width = 635
      inherited NANetFrameLinks: TNANetFrame
        Width = 631
        inherited StringGrid: TStringGrid
          Width = 631
        end
      end
    end
    inherited Panel1: TPanel
      Top = 409
      Width = 635
    end
  end
end
