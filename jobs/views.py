import csv
import urllib.parse
import time
import requests
from bs4 import BeautifulSoup
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets, status

from .models import Job
from .serializers import JobSerializer


@api_view(["GET"])
def import_jobs_from_csv(request):
    csv_file_path = "indeed_jobs.csv"

    try:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            inserted = 0
            skipped = 0

            for row in reader:
                # Normalize keys: remove leading/trailing spaces
                row = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

                # Skip duplicate records
                if Job.objects.filter(job_url=row["URL"]).exists():
                    skipped += 1
                    continue

                Job.objects.create(
                    title=row["Job Title"],
                    company=row["Company"],
                    location=row["Location"],
                    date_posted=row["Date Posted"],
                    summary=row["Summary"],
                    job_url=row["URL"],
                )

                inserted += 1

        return Response({
            "message": "Import completed",
            "inserted": inserted,
            "skipped_duplicates": skipped
        })

    except FileNotFoundError:
        return Response(
            {"error": "indeed_jobs.csv not found"},
            status=status.HTTP_400_BAD_REQUEST
        )

    

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    # Override list() to support filters
    def list(self, request, *args, **kwargs):
        city = request.query_params.get("city")
        position = request.query_params.get("position")

        queryset = self.queryset

        if city:
            queryset = queryset.filter(location__icontains=city)

        if position:
            queryset = queryset.filter(title__icontains=position)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    # retrieve() / create() / update() / destroy() are already handled by ModelViewSet



@api_view(["GET"])
def scrape_indeed(request):
    job_title = request.GET.get("title")
    city = request.GET.get("city")
    posted_within_days = request.GET.get("days", "1")

    if not job_title or not city:
        return Response(
            {"error": "Missing required params: title, city"},
            status=status.HTTP_400_BAD_REQUEST
        )

    job_title_encoded = urllib.parse.quote(job_title)
    city_encoded = urllib.parse.quote(city)

    base_url = f"https://www.indeed.com/jobs?q={job_title_encoded}&l={city_encoded}&fromage={posted_within_days}"
    headers = {"User-Agent": "Mozilla/5.0"}

    results = []
    page = 0

    while True:
        url = f"{base_url}&start={page}"
        print(f"Scraping: {url}")

        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
        except Exception as e:
            return Response({"error": f"Request failed: {str(e)}"}, status=500)

        soup = BeautifulSoup(res.text, "lxml")
        job_cards = soup.find_all("div", class_="cardOutline")

        if not job_cards:
            break

        for job in job_cards:
            title = job.find("h2", class_="jobTitle")
            company = job.find("span", class_="companyName")
            location = job.find("div", class_="companyLocation")
            summary = job.find("div", class_="job-snippet")
            date_posted = job.find("span", class_="date")
            link = job.find("a", href=True)

            results.append({
                "title": title.text.strip() if title else "N/A",
                "company": company.text.strip() if company else "N/A",
                "location": location.text.strip() if location else "N/A",
                "date_posted": date_posted.text.strip() if date_posted else "N/A",
                "summary": summary.text.strip() if summary else "N/A",
                "url": "https://www.indeed.com" + link["href"] if link else None
            })

        page += 10
        time.sleep(1)  # Prevent blocking

    return Response({"count": len(results), "results": results})


