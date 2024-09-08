from datetime import datetime, timedelta
import calendar

# Générer les jours pour un mois donné
def generate_calendar(planning):
    date_format = "%Y-%m-%d"

    calendar_date = datetime.strptime(planning[0]['date'], date_format).date()
    month = calendar_date.month
    year = calendar_date.year

    calendar_body = ''

    # Obtenir le premier jour du mois
    first_day = datetime(year, month, 1)
    starting_day = first_day.weekday()

    # Obtenir le nombre de jours dans le mois
    last_day = (datetime(year, month + 1, 1) - timedelta(days=1)).day

    date = 1
    # Boucle pour générer les lignes
    for i in range(6):
        calendar_body += "<tr>"
        # Boucle pour générer les cellules
        for j in range(5):
            if i == 0 and j < starting_day:
                if starting_day < 5:
                    calendar_body += "<td></td>"
            elif date > last_day:
                break
            else:
                # Vérifier si la date correspond à une entrée du planning
                formatted_date = f"{year}-{month:02d}-{date:02d}"
                users = []
                for entry in planning:
                    if entry["date"] == formatted_date:
                        users = entry["users"]
                        break
                # Générer la cellule avec les utilisateurs si applicable
                cell = f"<td>{date}<br>{'<br/>'.join(users)}</td>"
                calendar_body += cell
                date += 1
        # Si le premier jour du mois est un dimanche, on passe au Lundi
        if date == 1 and starting_day == 6:
            date += 1
        else:
            date += 2
        calendar_body += "</tr>"

    return {'data': calendar_body, 'month': calendar.month_name[month], 'year': year}