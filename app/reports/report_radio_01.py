from starlette.responses import Response

import xlsxwriter
import datetime
import io
from   urllib.parse import quote
from   app.core.logger import log
from   app.db.connect import select
from   app.config.app_config import REPORT_PATH


def get_select():
    return """
		select
		    e.prot_num as "Номер протокола",
			e.event_date as "Дата выступления",
			e.rfbn_id as  "Код области",
			b.name as "Область",
			e.channel_name as "Наименование радиоканала, социальной сети",
			e.speaker as "ФИО, должность выступающего",
			e.description as "Тема выступления, наименование программы, ссылка",
			employee as "Исполнитель"
		from radio_events e, loader.branch b
		where e.rfbn_id=case when :rfbn_id='00' then e.rfbn_id else :rfbn_id end
		and   to_char(e.event_date,'YYYY-MM')=:period
		and   e.rfbn_id||'00'=b.rfbn_id
		and e.status=2
		order by prot_num
    """

report_name = 'Сведения о выступлениях на телевидении, радио и в социальных сетях'
report_code = 'РД_01'

HEADER_ROW = 2
DATA_START_ROW = HEADER_ROW + 1
LINE_HEIGHT = 15


def report_01(params, filename=f"rep_{report_code}.xlsx"):
	start_time = datetime.datetime.now()
	s_date = start_time.strftime("%H:%M:%S")

	output = io.BytesIO()

	records = select(get_select(),params)
	log.debug(f'RADIO REPORT_01\n\tPARAMS: {params}\n\tRECORDS: {records}')

	safe_filename = quote(filename)

	with xlsxwriter.Workbook(output, {'in_memory': True}) as workbook:
		worksheet = workbook.add_worksheet("Отчет")

		if not records:
			worksheet.write(0, 0, "Нет данных для отчета")
			workbook.close() 

			excel_bytes = output.getvalue()
    
			return Response(
				excel_bytes,
				media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
				headers={
					"Content-Disposition": f"attachment; filename=report.xlsx; filename*=UTF-8''{safe_filename}"
				}
			)


		### ЗАГОЛОВКИ
		title_name_report = workbook.add_format({ "align": "left", "font_color": "black", "font_size": "14", "valign": "vcenter", "bold": True	})
		title_format_right = workbook.add_format({ "align": "right", "font_color": "black", "font_size": "14", "valign": "vcenter", "bold": True	})
		title_format_it = workbook.add_format({	"align": "right", "valign": "vcenter", "italic": True })
		header_format = workbook.add_format({ "bold": True, "align": "center", "font_size": "12", "valign": "vcenter", "border": 1, "bg_color": "#E0F7FF", "text_wrap": True })
		text_format = workbook.add_format({ "align": "left", "valign": "vjustify", "border": 1, "bg_color": "#f2f2f2" })
		number_format = workbook.add_format({ "align": "center", "valign": "vcenter", "border": 1, "bg_color": "#f2f2f2" })
		text_format_center = workbook.add_format({ "text_wrap": True, "align": "center", "valign": "vjustify", "border": 1, "bg_color": "#f2f2f2", "num_format": '@' })
		date_format = workbook.add_format({	"num_format": "dd/mm/yyyy", "align": "center", "valign": "vcenter", "border": 1, "bg_color": "#f2f2f2" })
		list_format = workbook.add_format({ "text_wrap": True, "align": "left", "valign": "vcenter", "border": 1 })
		##
		list_name_number = []
		list_name_date = ['Дата выступления']
		list_name_text = ["Область","Наименование радиоканала, социальной сети", "Исполнитель", "Тема выступления, наименование программы, ссылка", "ФИО, должность выступающего"]
		list_name_text_list = []
		list_name_text_center = ["Код области", "Номер протокола"]

		list_column_width =[11, 12, 14, 10, 45, 50, 40, 50, 35]
		# Пишем шапку и указываем ширину колонок
		worksheet.set_column(0, 1, list_column_width[0])
		worksheet.write(HEADER_ROW, 0, "№", header_format)
		for col_num, column_name in enumerate(records[0]):
			worksheet.write(HEADER_ROW, col_num+1, column_name, header_format)
			worksheet.set_column(col_num+1, col_num+2, list_column_width[col_num+1])
			# log.info(f'{col_num+1}. CREATE TITLE. {column_name}:{list_column_width[col_num]}')

		worksheet.set_row(0, 24)
		worksheet.set_row(1, 24)
		worksheet.set_row(HEADER_ROW, 50)  

		### ЗАПИСЬ
		for row_num, record in enumerate(records):
			worksheet.write( DATA_START_ROW + row_num, 0, row_num+1, text_format_center )
			for col_num, (column_name, value) in enumerate(record.items()):
				if any(column_name.lower() in name.lower() for name in list_name_date):
					worksheet.write( DATA_START_ROW + row_num, col_num+1, value, date_format )
				if any(column_name.lower() in name.lower() for name in list_name_number):
					if value is None:
						continue
					worksheet.write( DATA_START_ROW + row_num, col_num+1,float(value), number_format )
				if any(column_name.lower() in name.lower() for name in list_name_text):
					worksheet.write( DATA_START_ROW + row_num, col_num+1, value, text_format )
				if any(column_name.lower() in name.lower() for name in list_name_text_center):
					worksheet.write( DATA_START_ROW + row_num, col_num+1, value, text_format_center )

		stop_time = datetime.datetime.now().strftime("%H:%M:%S")

		worksheet.write(0, 0, report_name, title_name_report)
		worksheet.write(0, 7, report_code, title_format_right)
		worksheet.write(1, 7, f'Дата формирования: {start_time.strftime("%d.%m.%Y ")}({s_date} - {stop_time})', title_format_it)


	log.info(f'REPORT: {report_code}. Формирование отчета {filename} завершено ({s_date} - {stop_time}).')

	excel_bytes = output.getvalue()

	return Response(
		excel_bytes,
		media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		headers={
			"Content-Disposition": f"attachment; filename=report.xlsx; filename*=UTF-8''{safe_filename}"
		}
	)

