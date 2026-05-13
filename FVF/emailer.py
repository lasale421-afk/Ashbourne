import win32com.client
import os
outlook = win32com.client.Dispatch('Outlook.Application')
mail = outlook.CreateItem(0)
mail.To = 'ngeniteau@iliad-free.fr'
mail.Subject = '[Télématique] Top 10 Fraude Kilométrique'
mail.Body = 'Bonjour, veuillez trouver en pièce jointe le rapport hebdomadaire.'
mail.Attachments.Add(os.path.abspath('top10_fraude_2026-05-12.xlsx'))
mail.Display()
mail.Send()